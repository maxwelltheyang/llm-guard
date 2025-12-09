const express = require('express');
const jwt = require('jsonwebtoken');
require('dotenv').config();

// Configure environment variables
const JWT_SECRET = process.env.JWT_SECRET;

// Check if JWT_SECRET is set
if (!JWT_SECRET) {
  console.error('JWT_SECRET environment variable is not set.');
  process.exit(1);
}

// Initialize Express app
const app = express();

// Middleware to verify JWT and check admin flag
function authenticateJWT(req, res, next) {
  const authHeader = req.headers.authorization;

  if (authHeader) {
    const token = authHeader.split(' ')[1];

    jwt.verify(token, JWT_SECRET, (err, user) => {
      if (err) {
        return res.sendStatus(403); // Forbidden
      }

      req.user = user;
      req.isAdmin = user.admin || false; // Extracting admin flag from JWT payload
      next();
    });
  } else {
    res.sendStatus(401); // Unauthorized
  }
}

// Example of a protected route
app.get('/protected', authenticateJWT, (req, res) => {
  res.send(`This is a protected route. Admin access: ${req.isAdmin ? 'Yes' : 'No'}`);
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
