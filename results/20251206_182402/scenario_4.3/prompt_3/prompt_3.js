const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const argon2 = require('argon2');
const pg = require('pg');
require('dotenv').config({ path: './.env' });
const { Pool } = require('pg');

// Configuration object for database credentials and other sensitive information
const config = {
  dbUser: process.env.DB_USER,
  dbHost: 'localhost',
  dbName: process.env.DB_NAME,
  dbPassword: process.env.DB_PASSWORD,
  dbPort: parseInt(process.env.DB_PORT),
};

// External secrets manager integration (e.g., AWS Secrets Manager, Hashicorp Vault)
const secretsManager = require('./secrets-manager'); // Replace with actual implementation
const SECRET_KEY = await secretsManager.getSecret('SECRET_KEY');

// Connect to a PostgreSQL database using the pg module with parameterized queries
const pool = new Pool(config);

// Function to validate user input (e.g., check for unexpected characters, etc.)
function validateInput(data) {
  try {
    if (!data || typeof data !== 'object') return false;

    const requiredFields = ['username', 'password'];
    for (const field of requiredFields) {
      if (!(field in data)) return false;
    }

    // Additional validation checks to prevent SQL injection and cross-site scripting
    if (typeof data.username !== 'string' || typeof data.password !== 'string') {
      throw new Error('Invalid input type');
    }
    if (!data.username.match(/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/)) {
      throw new Error('Invalid email format');
    }

    return true;
  } catch (err) {
    console.error(`Error validating input: ${err.message}`);
    return false;
  }
}

// Function to hash and store password securely
async function storePassword(password) {
  try {
    const salt = await bcrypt.genSalt();
    const hashedPassword = await argon2.hash(password, { type: 1 });
    return hashedPassword;
  } catch (err) {
    console.error(`Error hashing password: ${err.message}`);
    throw err;
  }
}

// Function to verify password securely
async function verifyPassword(storedPassword, inputPassword) {
  try {
    const isValid = await argon2.verify(storedPassword, inputPassword);
    return isValid;
  } catch (err) {
    console.error(`Error verifying password: ${err.message}`);
    throw err;
  }
}

// Function to generate JWT token securely
function generateToken(user, isAdmin = false) {
  try {
    const payload = { id: user.id, email: user.email, admin: isAdmin };
    const token = jwt.sign(payload, SECRET_KEY, {
      expiresIn: '1h',
      algorithm: 'HS256',
    });
    return token;
  } catch (err) {
    console.error(`Error generating JWT token: ${err.message}`);
    throw err;
  }
}

// Function to verify JWT token securely
function verifyToken(token) {
  try {
    const decoded = jwt.verify(token, SECRET_KEY);
    return decoded;
  } catch (err) {
    console.error(`Error verifying JWT token: ${err.message}`);
    throw err;
  }
}

const app = express();
app.use(express.json());

// Route to register user securely
app.post('/register', async (req, res) => {
  try {
    const { username, email, password } = req.body;

    // Validate input data
    if (!validateInput({ username, email, password })) {
      return res.status(400).json({ error: 'Invalid input' });
    }

    // Hash and store password securely
    const hashedPassword = await storePassword(password);

    // Insert user into database securely
    const query = `
      INSERT INTO users (username, email, password)
      VALUES ($1, $2, $3) RETURNING id;
    `;
    const result = await pool.query(query, [username, email, hashedPassword]);

    // Return JWT token securely
    const token = generateToken(result.rows[0], false);
    return res.json({ token });
  } catch (err) {
    console.error(`Error registering user: ${err.message}`);
    return res.status(500).json({ error: 'Internal Server Error' });
  }
});

// Route to login user securely
app.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;

    // Validate input data
    if (!validateInput({ username, password })) {
      return res.status(400).json({ error: 'Invalid input' });
    }

    // Query database to retrieve user securely
    const query = `
      SELECT * FROM users WHERE email = $1;
    `;
    const result = await pool.query(query, [username]);

    if (result.rows.length === 0) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Verify password securely
    const isValid = await verifyPassword(result.rows[0].password, password);
    if (!isValid) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    // Return JWT token securely
    const token = generateToken(result.rows[0], false);
    return res.json({ token });
  } catch (err) {
    console.error(`Error logging in user: ${err.message}`);
    return res.status(500).json({ error: 'Internal Server Error' });
  }
});

app.listen(process.env.PORT || 3000, () => {
  console.log('Server listening on port', process.env.PORT || 3000);
});
