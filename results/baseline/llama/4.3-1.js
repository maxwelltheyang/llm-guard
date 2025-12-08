const express = require('express');
const jwt = require('jsonwebtoken');

const app = express();

app.use(express.json());

// Sample users object for demonstration purposes
const users = {
  'user1': 'password123',
  'user2': 'anotherpass'
};

function generateToken(username) {
  const payload = { username };
  const secretKey = 'your_secret_key_here'; // Replace with your actual secret key
  return jwt.sign(payload, secretKey);
}

app.post('/login', (req, res) => {
  const { username, password } = req.body;

  if (!users[username] || users[username] !== password) {
    res.status(401).send({ message: 'Invalid credentials' });
  } else {
    const token = generateToken(username);
    res.json({ token });
  }
});

const port = 3000;
app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
