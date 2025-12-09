const express = require('express');
const jwt = require('jsonwebtoken');
const Redis = require('ioredis');
require('dotenv').config();

// Configure environment variables
const JWT_SECRET = process.env.JWT_SECRET;
const JWT_EXPIRATION = process.env.JWT_EXPIRES_IN || '1h';

// Check if JWT_SECRET is set
if (!JWT_SECRET) {
  console.error('JWT_SECRET environment variable is not set.');
  process.exit(1);
}

// Initialize Express app
const app = express();

// Initialize Redis client for token blacklist
const redisClient = new Redis();

// Middleware to verify JWT and check admin flag
function authenticateJWT(req, res, next) {
  const authHeader = req.headers.authorization;

  if (authHeader) {
    const token = authHeader.split(' ')[1];

    // Check if the token is blacklisted
    redisClient.get(`blacklist_${token}`, (err, data) => {
      if (err) throw err;

      if (data) {
        return res.sendStatus(403); // Forbidden
      }

      jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) {
          return res.sendStatus(403); // Forbidden
        }

        req.user = user;
        req.isAdmin = user.admin || false; // Extracting admin flag from JWT payload
        next();
      });
    });
  } else {
    res.sendStatus(401); // Unauthorized
  }
}

// Route to simulate logging out by blacklisting the token
app.post('/logout', authenticateJWT, (req, res) => {
  const authHeader = req.headers.authorization;
  const token = authHeader.split(' ')[1];

  // Add the token to the blacklist with expiration
  redisClient.set(`blacklist_${token}`, true, 'EX', 60 * 60, (err) => { // 1 hour expiration
    if (err) {
      return res.status(500).json({ message: 'Error occurred during logout.' });
    }

    res.status(200).json({ message: 'Successfully logged out.' });
  });
});

// Example of a protected route
app.get('/protected', authenticateJWT, (req, res) => {
  res.send(`This is a protected route. Admin access: ${req.isAdmin ? 'Yes' : 'No'}`);
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
