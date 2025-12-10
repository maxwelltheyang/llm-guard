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
    const token = req.headers['x-access-token'];

    // Verify the JWT token using the secret key
    jwt.verify(token, secretKey, { audience: process.env.SECRET_KEY_AUDIENCE }, (err, decoded) => {
      if (err) {
        throw new Error('Invalid or expired token');
      }

      req.user = decoded;
      next();
    });
  } catch (err) {
    console.error(err);
    res.status(401).send({ error: 'Unauthorized' });
  }
};

// Middleware to validate token's issuer and audience
const validateTokenIssuerAudience = async (req, res, next) => {
  try {
    const token = req.headers['x-access-token'];

    // Verify the token's issuer and audience using the JWT library's verify function
    jwt.verify(token, secretKey, { audience: process.env.SECRET_KEY_AUDIENCE }, (err, decoded) => {
      if (err) {
        throw new Error('Invalid or expired token');
      }

      req.user = decoded;
      next();
    });
  } catch (err) {
    console.error(err);
    res.status(401).send({ error: 'Unauthorized' });
  }
};

// Middleware to handle specific exceptions in getDecryptionKeyFromDatabase
const handleExceptionInGetDecryptionKeyFromDatabase = async (req, res, next) => {
  try {
    const token = req.headers['x-access-token'];

    // Verify the JWT token using the secret key
    jwt.verify(token, secretKey, { audience: process.env.SECRET_KEY_AUDIENCE }, (err, decoded) => {
      if (err) {
        throw new Error('Invalid or expired token');
      }

      req.user = decoded;
      next();
    });
  } catch (err) {
    console.error(err);

    // Handle the specific exception
    if (err instanceof TimeoutError) {
      res.status(500).send({ error: 'Timeout while fetching decryption key' });
    } else {
      res.status(401).send({ error: 'Unauthorized' });
    }
  }
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
  console.error(err);
}

// Make the admin flag available in the middleware
const makeAdminAvailable = async (req, res, next) => {
  if (req.user && req.user.admin === true) {
    req.isAdmin = true;
  }

  next();
};

app.use(makeAdminAvailable);

app.get('/protected', authenticateJWT, validateTokenIssuerAudience, handleExceptionInGetDecryptionKeyFromDatabase, async (req, res) => {
  try {
    // Proceed with protected route logic
  } catch (err) {
    console.error(err);

    // Log the error in production environments
    if (process.env.NODE_ENV === 'production') {
      logger.error(err);
    }

    // Propagate the error to the client
    res.status(500).send({ error: 'Internal Server Error' });
  }
});

app.listen(3000, () => {
  console.log('Server listening on port 3000');
});
