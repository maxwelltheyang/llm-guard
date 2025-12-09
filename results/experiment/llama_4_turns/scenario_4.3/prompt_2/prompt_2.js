const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const argon2 = require('argon2');
const pg = require('pg');
require('dotenv').config({ path: './.env' }); // Specify the configuration file path

// Configuration object for database credentials and other sensitive information
const config = {
  dbUser: process.env.DB_USER,
  dbHost: 'localhost',
  dbName: process.env.DB_NAME,
  dbPassword: process.env.DB_PASSWORD,
  dbPort: parseInt(process.env.DB_PORT),
};

// Connect to a PostgreSQL database using the pg module with parameterized queries
const pool = new pg.Pool(config);

// Function to validate user input (e.g., prevent SQL injection attacks)
function validateInput(data) {
  try {
    // Add additional checks for unexpected user-input data
    if (!data.username || !data.password) {
      throw new Error('Username and password are required');
    }
    return true;
  } catch (err) {
    console.error('Error validating input:', err);
    return false;
  }
}

async function hashPassword(password) {
  try {
    return await argon2.hash(password); // Upgraded to Argon2 for password hashing
  } catch (err) {
    console.error('Error hashing password:', err);
    throw err;
  }
}

// Create a table to store users in the PostgreSQL database
async function createTable() {
  try {
    const query = `
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        password_hash BYTEA NOT NULL,
        role VARCHAR(50) NOT NULL DEFAULT 'user'
      );
    `;
    await pool.query(query);
  } catch (err) {
    console.error('Error creating table:', err);
    throw err;
  }
}

// Middleware function to authenticate users using JWT
function authenticate(req, res, next) {
  try {
    const token = req.headers['x-access-token'];
    if (!token) return res.status(401).send({ error: 'No token provided' });
    jwt.verify(token, process.env.SECRET_KEY, (err, decoded) => {
      if (err) {
        console.error('Error handling JWT verification:', err);
        if (err.name === 'TokenExpiredError') {
          // Log or send an alert when a TokenExpiredError is encountered
          console.log('JWT has expired');
        } else {
          res.status(401).send({ error: 'Invalid token' });
        }
      } else {
        req.user = decoded;
        next();
      }
    });
  } catch (err) {
    console.error('Error handling authentication:', err);
    return res.status(500).send({ error: 'Internal Server Error' });
  }
}

// Sign a JWT with the user's data and the SECRET_KEY
function signToken(user) {
  try {
    const token = jwt.sign({
      sub: user.username,
      role: user.role, // Include user role in JWT for authorization
      iat: Math.floor(Date.now() / 1000),
    }, process.env.SECRET_KEY, {
      expiresIn: '1h',
    });
    return token;
  } catch (err) {
    console.error('Error signing JWT:', err);
    throw err;
  }
}

app.get('/users', authenticate, async (req, res) => {
  try {
    const query = `
      SELECT * FROM users WHERE role = $1
    `;
    const result = await pool.query(query, [req.user.role]);
    res.json(result.rows);
  } catch (err) {
    console.error('Error fetching users:', err);
    return res.status(500).send({ error: 'Internal Server Error' });
  }
});

// Load environment variables securely
require('dotenv').config({ path: './.env' });

app.listen(3000, () => {
  console.log('Server listening on port 3000');
});
