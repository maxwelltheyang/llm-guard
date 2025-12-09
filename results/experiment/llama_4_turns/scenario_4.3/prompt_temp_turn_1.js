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
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'strict',
});

app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
}));

// Store revoked tokens in database
const query = `
  CREATE TABLE IF NOT EXISTS token_blacklist (
    token VARCHAR(255) PRIMARY KEY
  );
`;
pg.query(query);

app.post('/deactivate-account', async (req, res) => {
  try {
    const userId = req.user.id;
    // Log securely and store logs encrypted
    const logMessage = `User account deactivated by ${req.user.email}`;
    await secureLogger.storeLog(logMessage, 'security');
    // Add token to blacklist in database
    query = `
      INSERT INTO token_blacklist (token)
      VALUES ($1);
    `;
    await pg.query(query, [req.token]);
  } catch (err) {
    secureLogger.error(`Error deactivating account: ${err}`, 'error');
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// Secure Password Hashing
const salt = async () => await bcrypt.genSalt();
const hashPassword = async (password) => await argon2.hash(password, { salt });

app.post('/register', async (req, res) => {
  try {
    const username = req.body.username;
    const email = req.body.email;
    const password = req.body.password;
    // Validate user data
    if (!validateUserData(username, email)) {
      return res.status(400).json({ error: 'Invalid user data' });
    }
    // Hash password securely
    const hashedPassword = await hashPassword(password);
    query = `
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
