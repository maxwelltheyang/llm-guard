const express = require('express');
const bcrypt = require('bcryptjs'); 
const jwt = require('jsonwebtoken');
const dotenv = require('dotenv'); 
dotenv.config(); 

// Secret key for signing the JWT (set as an environment variable)
const secretKey = process.env.SECRET_KEY;

try {
  if (!secretKey || !secretKey.trim()) {
    throw new Error('SECRET_KEY environment variable not set or empty');
  }
} catch (error) {
  console.error(error.message);
}

if (typeof secretKey !== 'string') {
  console.error('SECRET_KEY must be a string');
  process.exit(1);
}

const { Pool } = require('pg'); // Using pg instead of pg-promise
const db = require('./db');

// Function to securely store passwords with salt
async function storePassword(password, email, id) {
  const saltRounds = 10;

  // Hash the password using bcrypt before storing it in the database
  const hashedPassword = await bcrypt.hash(password);

  try {
    // Create a new pool connection
    const pool = new Pool({
      connectionString: process.env.DB_URL,
    });

    // Use parameterized queries to prevent SQL injection attacks
    const result = await pool.query(
      `INSERT INTO users (email, password, id) VALUES ($1, $2, $3) RETURNING *`,
      [email, hashedPassword, id]
    );

    return { id: result.rows[0].id };
  } catch (err) {
    console.error(err);
    throw err;
  }
}

// Middleware to authenticate JWT
function authenticateJWT(req, res, next) {
  const authHeader = req.header('Authorization');
  if (!authHeader) {
    return res.status(401).send({ error: 'Unauthorized' });
  }

  const token = authHeader.split(' ')[1];
  if (!token) {
    return res.status(401).send({ error: 'Unauthorized' });
  }

  try {
    const decoded = jwt.verify(token, secretKey);
    req.user = { id: decoded.id };
    next();
  } catch (err) {
    console.error(err);
    return res.status(403).send({ error: 'Invalid token' });
  }
}

// Function to securely retrieve sensitive data from an encrypted database or secrets manager
const AWS = require('aws-sdk');
const vaultUrl = process.env.VAULT_URL;
const vaultToken = process.env.VAULT_TOKEN; // Added token for authentication

function getDecryptionKeyFromDatabase() {
  const params = {
    SecretId: vaultUrl,
    VersionStage: 'AWSCURRENT',
    IncludeDecryptionKeys: true,
  };

  return new Promise((resolve, reject) => {
    const client = new AWS.SecretsManager({ region: process.env.AWS_REGION });

    client.getSecretValue(params, (err, data) => {
      if (err) {
        console.error(err);
        reject(err);
      } else {
        try {
          // Extract the decryption key from the response
          const { SecretString } = data.SecretBinary;
          resolve(SecretString);
        } catch (e) {
          console.error(e);
          reject(e);
        }
      }
    });
  });
}

// Input validation for user-provided data
function validateInput(input) {
  // Basic input validation using express-validator
  const { body, query, params } = require('express-validator');

  const rules = [
    body('email').isEmail().withMessage('Invalid email'),
    body('password').isLength({ min: 8 }).withMessage('Password must be at least 8 characters long'),
    body('id').isInt().withMessage('Invalid ID'),
  ];

  try {
    // Run the validation rules
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      throw new Error('Validation failed');
    }
  } catch (err) {
    console.error(err);
    return false;
  }

  return true;
}

// Protect routes from potential SQL injection attacks
app.use(validateInput);

// Protected routes
app.get('/protected', async (req, res) => {
  if (!req.user) {
    return res.status(401).send({ error: 'Unauthorized' });
  }

  try {
    res.send({ message: `Hello!` });
  } catch (err) {
    console.error(err);
    return res.status(500).send({ error: 'Internal Server Error' });
  }
});

app.listen(3000, () => {
  console.log('Server listening on port 3000');
});
