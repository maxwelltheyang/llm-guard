const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const bodyParser = require('body-parser');
require('dotenv').config();

// Configure to use a scalable storage like Redis for blacklisting tokens
// const Redis = require('ioredis');
// const redisClient = new Redis();

const app = express();
const port = 3000;
const SECRET_KEY = process.env.JWT_SECRET_KEY;

// Throw error if secret key is not defined
if (!SECRET_KEY) {
    throw new Error('JWT secret key is not defined. Please set JWT_SECRET_KEY in your environment variables.');
}

// Mocked user data - in real scenarios, this data would come from a database
const users = [
    {
        id: 1,
        username: 'user1',
        password: '$2b$10$CwTycUXWue0Thq9StjUM0uJ8t4fj5gdjUgrrlqX9hZh6r5ozV/O2e', // bcrypt hash for 'password123'
        isAdmin: true
    },
    {
        id: 2,
        username: 'user2',
        password: '$2b$10$CwTycUXWue0Thq9StjUM0uJ8t4fj5gdjUgrrlqX9hZh6r5ozV/O2e', // bcrypt hash for 'password123'
        isAdmin: false
    }
];

// In-memory store for blacklisted tokens
const blacklistedTokens = new Set();

app.use(bodyParser.json());

// JWT authentication middleware
function authenticateJWT(req, res, next) {
    const authHeader = req.headers.authorization;

    if (!authHeader) {
        return res.status(401).json({ message: 'Authorization header is missing' });
    }

    const token = authHeader.split(' ')[1];

    // Check if token is blacklisted
    if (blacklistedTokens.has(token)) {
        return res.status(403).json({ message: 'Token has been invalidated' });
    }

    jwt.verify(token, SECRET_KEY, (err, decoded) => {
        if (err) {
            return res.status(403).json({ message: 'Token is not valid' });
        }
        // Add user object and admin status to the request
        req.user = { id: decoded.id, username: decoded.username, isAdmin: decoded.isAdmin };
        next();
    });
}

app.post('/login', async (req, res) => {
    const { username, password } = req.body;

    const user = users.find(u => u.username === username);
    if (!user) {
        return res.status(401).json({ message: 'Authentication failed. Wrong username or password.' });
    }

    const passwordMatch = await bcrypt.compare(password, user.password);
    if (!passwordMatch) {
        return res.status(401).json({ message: 'Authentication failed. Wrong username or password.' });
    }

    const token = jwt.sign({ id: user.id, username: user.username, isAdmin: user.isAdmin }, SECRET_KEY, { expiresIn: '1h' });
    res.json({ message: 'Authentication successful!', token });
});

// Logout endpoint
app.post('/logout', authenticateJWT, (req, res) => {
    const authHeader = req.headers.authorization;
    const token = authHeader.split(' ')[1];

    // Blacklist the token
    blacklistedTokens.add(token);

    // This would be a more scalable implementation using Redis, with a TTL matching token expiry
    // redisClient.set(token, 'blacklisted', 'EX', 3600);

    res.json({ message: 'Logout successful!' });
});

// Protected route
app.get('/protected', authenticateJWT, (req, res) => {
    res.json({ message: 'This is a protected route', user: req.user });
});

// Admin-only route
app.get('/admin', authenticateJWT, (req, res) => {
    if (!req.user.isAdmin) {
        return res.status(403).json({ message: 'Access denied. Admins only.' });
    }
    res.json({ message: 'This is an admin route', user: req.user });
});

app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
