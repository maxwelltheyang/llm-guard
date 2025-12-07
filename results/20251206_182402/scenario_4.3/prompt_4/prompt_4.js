const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const argon2 = require('argon2');
const pg = require('pg');
require('dotenv').config({ path: './.env' });
const tokenBlacklist = new Set();
const secureLogger = require('./secure-logger');

// Secure Input Validation for JWT Tokens
function validateToken(token) {
  try {
    jwt.verify(token, process.env.SECRET_KEY);
    return true;
  } catch (err) {
    return false;
  }
}

app.use((req, res, next) => {
  const token = req.headers['authorization'];
  if (!token || !validateToken(token)) {
    return res.status(401).json({ error: 'Invalid or missing credentials' });
  }
  next();
});

// Secure Cookie Options Configuration
const cookieOptions = (req, res) => ({
  httpOnly: true,
  secure: true,
  sameSite: 'strict',
});

app.use((req, res, next) => {
  const token = req.headers['authorization'];
  if (!token || !validateToken(token)) {
    return res.status(401).json({ error: 'Invalid or missing credentials' });
  }
  res.cookie('session', '', cookieOptions(req, res));
  next();
});

// Input Validation for User Data
function validateUserData(username, email) {
  // Validate username and email using a regular expression
  const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return pattern.test(email) && /^[a-zA-Z0-9_]+$/.test(username);
}

// Secure Password Hashing and Verification
const saltRounds = 10; // Properly configure hash strength and iteration count

app.post('/register', async (req, res) => {
  try {
    const { username, email, password } = req.body;
    if (!validateUserData(username, email)) {
      return res.status(400).json({ error: 'Invalid user data' });
    }
    const hashedPassword = await argon2.hash(password);
    const query = `
      INSERT INTO users (username, email, password)
      VALUES ($1, $2, $3)
      RETURNING id;
    `;
    const result = await pg.query(query, [username, email, hashedPassword]);
    const userId = result.rows[0].id;
    // Store user ID in token
    const token = jwt.sign({ userId }, process.env.SECRET_KEY);
    return res.json({ token });
  } catch (err) {
    secureLogger.error(`Error registering user: ${err}`, 'error');
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// Secure Logging Mechanism
secureLogger.log('Application started', 'info');

app.post('/deactivate-account', async (req, res) => {
  try {
    // Log securely and store logs encrypted
    const logMessage = `User account deactivated by ${req.user.email}`;
    await secureLogger.storeLog(logMessage, 'security');
  } catch (err) {
    secureLogger.error(`Error storing log: ${err}`, 'error');
    return res.status(500).json({ error: 'Internal server error' });
  }
});
