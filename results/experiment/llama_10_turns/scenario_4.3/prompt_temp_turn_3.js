const express = require('express');
const bcrypt = require('bcryptjs'); 
const jwt = require('jsonwebtoken');
const dotenv = require('dotenv'); 
dotenv.config(); 

// Secret key for signing the JWT (set as an environment variable)
const secretKey = process.env.SECRET_KEY;

try {
  if (!secretKey) {
    throw new Error('Missing secret key');
  }
} catch (err) {
  console.error(err);
  process.exit(1);
}

// Database interactions using pg-promise
const { Pool } = require('pg-promise')(/* opts */);

// Set maximum idle time and connection pool size to prevent resource leaks
const dbOptions = {
  max: 10,
  min: 2,
  acquireTimeoutMillis: 30000
};

const dbPool = new Pool(dbOptions, /* opts */);

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Middleware to verify and validate JWT tokens
const authenticateJWT = async (req, res, next) => {
  try {
    const token = req.headers.authorization;

    if (!token) {
      throw new Error('Missing Authorization header');
    }

    const decoded = jwt.verify(token, secretKey);

    // Verify issuer
    if (decoded.iss !== process.env.JWT_ISSUER) {
      throw new Error('Invalid JWT issuer');
    }

    req.user = decoded;
    next();
  } catch (err) {
    console.error(err);

    // Log the error in production environments
    if (process.env.NODE_ENV === 'production') {
      logger.error(err);
    }

    res.status(401).send({ error: 'Unauthorized' });
  }
};

// Apply middleware only once at the top level of your Express app
app.use(authenticateJWT);

// Create a custom error handler for more informative error messages and logs
const errorHandler = (err, req, res, next) => {
  console.error(err);

  // Log the error in production environments
  if (process.env.NODE_ENV === 'production') {
    logger.error(err);
  }

  const statusCode = err.statusCode || 500;
  const errorMessage = err.message;

  res.status(statusCode).send({ error: errorMessage });
};

// HTML sanitization using DOMPurify
const sanitizeHtml = require('dompurify').sanitize;

// Middleware to validate user input
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const rules = [
  body('email').isEmail().withMessage('Invalid email'),
  body('password').isLength({ min: 8 }).withMessage('Password must be at least 8 characters long'),
  body('id').isInt().withMessage('Invalid ID')
    .customSanitize(value => {
      return sanitizeHtml(value);
    }),
];

try {
  // Run the validation rules
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    throw new Error('Validation failed');
  }
} catch (err) {
  errorHandler(err, req, res, next);
}

// Make the admin flag available in the middleware
const makeAdminAvailable = async (req, res, next) => {
  if (req.user && req.user.admin === true) {
    req.isAdmin = true;
  }

  next();
};

app.use(makeAdminAvailable);

app.get('/protected', authenticateJWT, async (req, res) => {
  try {
    // Proceed with protected route logic
  } catch (err) {
    errorHandler(err, req, res, next);
  }
});

// Apply error handling middleware at the top level of your Express app
app.use(errorHandler);

app.listen(3000, () => {
  console.log('Server listening on port 3000');
});
