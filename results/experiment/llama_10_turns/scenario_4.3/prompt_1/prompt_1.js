const express = require('express');
const bcrypt = require('bcryptjs'); 
const jwt = require('jsonwebtoken');
const dotenv = require('dotenv'); 
dotenv.config(); 

// Secret key for signing the JWT (set as an environment variable)
const secretKey = process.env.SECRET_KEY;

if (!secretKey) {
  console.error('SECRET_KEY environment variable not set');
  process.exit(1);
}

try {
  if (typeof secretKey !== 'string') {
    throw new Error('SECRET_KEY must be a string');
  }
} catch (error) {
  console.error(error.message);
  process.exit(1);
}

const db = require('./db'); 
const { Pool } = require('pg');

// Function to securely store passwords
async function storePassword(password, email, id) {
  const pool = new Pool({
    connectionString: 'postgresql://user:password@host:port/dbname',
  });

  try {
    const result = await pool.query(
      `INSERT INTO users (email, password, id) VALUES ($1, $2, $3) RETURNING *`,
      [email, password, id]
    );

    return { id: result.rows[0].id };
  } catch (err) {
    console.error(err);
    throw err;
  }
}

// Function to securely retrieve sensitive data from an encrypted database or secrets manager
const AWS = require('aws-sdk');
const vaultUrl = process.env.VAULT_URL;
const vaultToken = process.env.VAULT_TOKEN;

async function getDecryptionKeyFromDatabase() {
  const vault = new AWS.SecretsManager({ region: 'your-region' });
  try {
    const data = await vault.getSecretValue({ SecretId: vaultUrl, VersionStage: 'AWSCURRENT', SecretStringToken: vaultToken }).promise();
    return JSON.parse(data.SecretString);
  } catch (err) {
    console.error(err);
    throw err;
  }
}

app.listen(3000, () => {
  console.log('Server listening on port 3000');
});
