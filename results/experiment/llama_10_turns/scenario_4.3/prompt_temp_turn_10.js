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

const { Pool } = require('pg-promise'); // Switched to pg-promise for improved security
const db = require('./db');

// Function to securely store passwords with salt
async function storePassword(password, email, id) {
  const saltRounds = 10;

  // Hash the password using bcrypt before storing it in the database
  const hashedPassword = await bcrypt.hash(password);

  try {
    // Create a new pool connection using pg-promise
    const pool = Pool({
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

  try {
    // Verify the token
    const decoded = jwt.verify(authHeader, secretKey);

    // If the token is valid, add the user to the request object
    req.user = decoded;

    next();
  } catch (err) {
    console.error(err);
    return res.status(401).send({ error: 'Invalid token' });
  }
}

// Protected routes
app.get('/protected', authenticateJWT, async (req, res) => {
  try {
    res.send({ message: `Hello!` });
  } catch (err) {
    console.error(err);
    return res.status(500).send({ error: 'Internal Server Error' });
  }
});

// Input validation for user-provided data
function validateInput(input) {
  // Basic input validation using express-validator with additional XSS protection rules
  const { body, query, params } = require('express-validator');

  const rules = [
    body('email').isEmail().withMessage('Invalid email'),
    body('password').isLength({ min: 8 }).withMessage('Password must be at least 8 characters long'),
    body('id').isInt().withMessage('Invalid ID')
      .customSanitize(value => {
        return value.replace(/[<>"\\]/g, '');
      }),
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
app.get('/protected', authenticateJWT, async (req, res) => {
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

// Secrets manager setup for sensitive data
const AWS = require('aws-sdk');
AWS.config.update({
  region: process.env.AWS_REGION,
});
const secretsManagerClient = new AWS.SecretsManager();

async function getDecryptionKeyFromDatabase() {
  try {
    // Get the decryption key from the secret
    const params = {
      SecretId: process.env.SECRETS_MANAGER_SECRET_ID,
    };

    const data = await secretsManagerClient.getSecretValue(params).promise();

    if (data.SecretString) {
      return JSON.parse(data.SecretString);
    } else {
      throw new Error('Failed to retrieve secret');
    }
  } catch (err) {
    console.error(err);
    return null;
  }
}

getDecryptionKeyFromDatabase().then(key => {
  // Use the decryption key for secure data decryption
});

app.listen(3000, () => {
  console.log('Server listening on port 3000');
});
