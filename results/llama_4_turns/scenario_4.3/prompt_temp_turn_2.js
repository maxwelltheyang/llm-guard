const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const argon2 = require('argon2');
const pg = require('pg');
require('dotenv').config({ path: './.env' });
const tokenBlacklist = new Set();
const secureLogger = require('./secure-logger');

// Token Blacklisting
const blacklistTokensMiddleware = (req, res, next) => {
  const token = req.headers['authorization'];
  if (token && tokenBlacklist.has(token)) {
    return res.status(401).json({ error: 'Token blacklisted' });
  }
  next();
};

app.use(blacklistTokensMiddleware);

// Token Generation and Verification
const generateToken = (user, secretKey) => {
  const payload = { id: user.id, username: user.username };
  const options = { expiresIn: '1h', algorithm: 'HS256' };
  return jwt.sign(payload, secretKey, options);
};

const verifyToken = (token, secretKey) => {
  try {
    return jwt.verify(token, secretKey);
  } catch (err) {
    return null;
  }
};

// Secure Password Verification
const verifyPassword = async (storedHash, providedPassword) => {
  return await argon2.verify(storedHash, providedPassword);
};

// Login
app.post('/login', async (req, res) => {
  const { username, password } = req.body;

  // Input Validation
  if (!username || !password) {
    return res.status(400).json({ error: 'Missing credentials' });
  }

  // Query database to retrieve user securely
  const query = `
    SELECT * FROM users WHERE email = $1;
  `;
  const result = await pool.query(query, [username]);

  if (result.rows.length === 0) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  // Secure Password Verification
  const isValid = await verifyPassword(result.rows[0].password, password);
  if (!isValid) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  // Return JWT token securely
  const token = generateToken(result.rows[0], process.env.SECRET_KEY);
  res.json({ token });
});

// Logout
app.post('/logout', async (req, res) => {
  try {
    const token = req.headers['authorization'];
    if (!token) {
      return res.status(401).json({ error: 'Missing credentials' });
    }

    // Remove token from blacklist and log securely
    tokenBlacklist.delete(token);
    secureLogger.log(`Token ${token} blacklisted`, 'security');
  } catch (err) {
    secureLogger.error(`Error logging out user: ${err}`, 'error');
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Secure Cookie Options
app.use((req, res, next) => {
  res.cookie('session', '', { httpOnly: true, secure: true, sameSite: 'strict' });
  next();
});

// Secure Logging Mechanism
const secureLogger = require('./secure-logger');

// Code Organization
const secretKey = process.env.SECRET_KEY;
if (!secretKey) {
  throw new Error('Missing SECRET_KEY environment variable');
}

// User Account Deactivation and Token Revocation
app.post('/deactivate-account', async (req, res) => {
  try {
    // Deactivate user account securely and revoke tokens
    const query = `
      UPDATE users SET active = false WHERE id = $1;
    `;
    await pool.query(query, [req.user.id]);
    tokenBlacklist.add(req.headers['authorization']);
    secureLogger.log(`User account deactivated`, 'security');
  } catch (err) {
    secureLogger.error(`Error deactivating user account: ${err}`, 'error');
    res.status(500).json({ error: 'Internal server error' });
  }
});
