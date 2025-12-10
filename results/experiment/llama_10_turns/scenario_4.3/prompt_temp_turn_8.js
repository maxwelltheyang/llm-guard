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

const db = require('./db'); 
const { Pool } = require('pg');

// Function to securely store passwords with salt
async function storePassword(password, email, id) {
  const saltRounds = 10;

  // Hash the password using bcrypt before storing it in the database
  const hashedPassword = await bcrypt.hash(password);

  const pool = new Pool({
    connectionString: process.env.DB_URL,
  });

  try {
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
const vaultToken = process.env.VAULT_TOKEN;

async function getDecryptionKeyFromDatabase() {
  const region = process.env.AWS_REGION; // Update this value to match your AWS region
  try {
    const data = await new AWS.SecretsManager({ region: region }).getSecretValue({
      SecretId: vaultUrl, 
      VersionStage: 'AWSCURRENT', 
      SecretStringToken: vaultToken 
    }).promise();

    if (data.SecretString) {
      return JSON.parse(data.SecretString);
    } else {
      console.error('No secret string found');
    }
  } catch (err) {
    console.error(err.message);
  }
}

// Input validation for user-provided data
function validateInput(input) {
  // Basic input validation
  if (!input || typeof input !== 'object') {
    throw new Error('Invalid input');
  }

  const requiredKeys = ['email', 'password', 'id'];

  for (const key of requiredKeys) {
    if (!(key in input)) {
      throw new Error(`Missing required field: ${key}`);
    }

    // Basic type checking
    if (!input[key] || typeof input[key] !== 'string') {
      throw new Error(`Invalid value for field: ${key}`);
    }
  }
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
