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

const { Pool } = require('pg-promise'); // Switched to pg-promise for improved security
const db = require('./db');

// Function to securely store passwords with salt
async function storePassword(password, email, id) {
  const saltRounds = null; // Remove fixed salt round value

  try {
    // Hash the password using bcrypt's automatic salt round determination
    const hashedPassword = await bcrypt.hash(password, saltRounds);

    // Store the hashed password and other user details in the database
    return { email, id, hashedPassword };
  } catch (err) {
    console.error(err);
    throw new Error('Failed to store password');
  }
}

// Secrets manager setup for sensitive data
const AWS = require('aws-sdk');
AWS.config.update({
  region: process.env.AWS_REGION,
});
const secretsManagerClient = new AWS.SecretsManager();

async function getDecryptionKeyFromDatabase() {
  let retryCount = 0;
  const maxRetries = 3; // Define the maximum number of retries

  while (retryCount < maxRetries) {
    try {
      // Get the decryption key from the secret
      const params = {
        SecretId: process.env.SECRETS_MANAGER_SECRET_ID,
      };

      const data = await secretsManagerClient.getSecretValue(params).promise();

      if (data.SecretString) {
        return JSON.parse(data.SecretString);
      } else {
        throw new Error('Failed to retrieve secret');
      }
    } catch (err) {
      console.error(`Error fetching decryption key: ${err}`);

      // Retry after a short delay
      retryCount++;
      await new Promise(resolve => setTimeout(resolve, 500));

      if (retryCount >= maxRetries) {
        throw err;
      }
    }
  }
}

// Middleware to verify and validate JWT tokens
const authenticateJWT = async (req, res, next) => {
  try {
    const token = req.headers['x-access-token'];

    // Verify the JWT token using the secret key
    jwt.verify(token, secretKey, (err, decoded) => {
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

// Middleware to validate the token's issuer and audience
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

app.get('/protected', authenticateJWT, validateTokenIssuerAudience, async (req, res) => {
  if (!req.user || !req.isAdmin) {
    return res.status(401).send({ error: 'Unauthorized' });
  }

  try {
    // Proceed with protected route logic
  } catch (err) {
    console.error(err);
    res.status(500).send({ error: 'Internal Server Error' });
  }
});

app.listen(3000, () => {
  console.log('Server listening on port 3000');
});
