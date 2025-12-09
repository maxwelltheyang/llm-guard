const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');

const app = express();
app.use(express.json());

// Import environment variables using dotenv
require('dotenv').config();

// Connect to a PostgreSQL database using the pg module
const { Pool } = require('pg');

const dbConfig = {
  user: process.env.DB_USER,
  host: 'localhost',
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  port: parseInt(process.env.DB_PORT),
};

const pool = new Pool(dbConfig);

async function hashPassword(password) {
  try {
    return await bcrypt.hash(password, 10);
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
        password_hash BYTEA NOT NULL
      );
    `;
    await pool.query(query);
  } catch (err) {
    console.error('Error creating table:', err);
  }
}

// Populate the users table with some initial data for testing purposes
async function populateTable() {
  try {
    const query = `
      INSERT INTO users (username, password_hash)
      VALUES ($1, $2)
      ON CONFLICT DO NOTHING;
    `;
    await pool.query(query, ['user1', await hashPassword('password1')]);
  } catch (err) {
    console.error('Error populating table:', err);
  }
}

// Initialize the database and populate it with some data
async function initDB() {
  try {
    await createTable();
    await populateTable();
  } catch (err) {
    console.error('Error initializing database:', err);
  }
}

initDB();

app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(401).send({ error: 'Invalid username or password' });
  }

  try {
    // Retrieve the user's data from the PostgreSQL database
    const query = `
      SELECT password_hash FROM users WHERE username = $1;
    `;
    const result = await pool.query(query, [username]);
    if (result.rows.length === 0) {
      return res.status(401).send({ error: 'Invalid username or password' });
    }
    const userPasswordHash = result.rows[0].password_hash;

    // Verify the user's password
    if (!await bcrypt.compare(password, userPasswordHash)) {
      return res.status(401).send({ error: 'Invalid username or password' });
    }

    // Retrieve the SECRET_KEY environment variable
    const secretKey = process.env.SECRET_KEY;
    if (!secretKey) {
      return res.status(500).send({ error: 'SECRET_KEY environment variable not set' });
    }

    // Sign a JWT with the user's data and the SECRET_KEY
    const token = jwt.sign({
      sub: username,
      iat: Math.floor(Date.now() / 1000),
    }, secretKey, {
      expiresIn: '1h',
    });

    res.json({ token });
  } catch (err) {
    console.error('Error handling login request:', err);
    res.status(500).send({ error: 'Internal Server Error' });
  }
});

app.listen(3000, () => {
  console.log('Server listening on port 3000');
});
