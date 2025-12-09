const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const bodyParser = require('body-parser');
require('dotenv').config();

const app = express();
const port = 3000;
const SECRET_KEY = process.env.JWT_SECRET_KEY;

// Throw error if secret key is not defined
if (!SECRET_KEY) {
    throw new Error('JWT secret key is not defined. Please set JWT_SECRET_KEY in your environment variables.');
}

// Mocked user data - in real scenarios, query the database
const users = [
    {
        id: 1,
        username: 'user1',
        password: '$2b$10$CwTycUXWue0Thq9StjUM0uJ8t4fj5gdjUgrrlqX9hZh6r5ozV/O2e' // bcrypt hash for 'password123'
    }
];

app.use(bodyParser.json());

// JWT authentication middleware
function authenticateJWT(req, res, next) {
    const authHeader = req.headers.authorization;

    if (!authHeader) {
        return res.status(401).json({ message: 'Authorization header is missing' });
    }

    const token = authHeader.split(' ')[1];

    jwt.verify(token, SECRET_KEY, (err, user) => {
        if (err) {
            return res.status(403).json({ message: 'Token is not valid' });
        }
        req.user = user;
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

    const token = jwt.sign({ id: user.id, username: user.username }, SECRET_KEY, { expiresIn: '1h' });
    res.json({ message: 'Authentication successful!', token });
});

// Protected route
app.get('/protected', authenticateJWT, (req, res) => {
    res.json({ message: 'This is a protected route', user: req.user });
});

app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
