const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const bodyParser = require('body-parser');
require('dotenv').config();

// User database simulation
// In a real-world scenario, use an actual database for storing users
const usersDB = [
  {
    id: 1,
    username: 'user1',
    passwordHash: bcrypt.hashSync('password123', 10) // Store hashed password
  }
];

// Configure environment variables
const JWT_SECRET = process.env.JWT_SECRET;
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '1h';

// Check if JWT_SECRET is set
if (!JWT_SECRET) {
  console.error('JWT_SECRET environment variable is not set.');
  process.exit(1);
}

// Initialize Express app
const app = express();
app.use(bodyParser.json());

// Login function
app.post('/login', async (req, res) => {
  const { username, password } = req.body;

  // Check if user exists
  const user = usersDB.find(u => u.username === username);
  if (!user) {
    return res.status(401).json({ message: 'Invalid username or password' });
  }

  // Validate password
  const isPasswordCorrect = await bcrypt.compare(password, user.passwordHash);
  if (!isPasswordCorrect) {
    return res.status(401).json({ message: 'Invalid username or password' });
  }

  // Issue JWT token
  const token = jwt.sign({ userId: user.id }, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });

  // Respond with token
  res.status(200).json({ token });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
