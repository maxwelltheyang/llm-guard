const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const app = express();
app.use(express.json());

const users = [
  { id: 1, username: 'user1', password: '$2b$10$g7E9l9Rg3IAgxZpGZW9GQucHFsC1mXZ8iGjYF.fODSW1b1tHO4b26' } // password: 'password123'
];

const secretKey = 'your_jwt_secret_key';

app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  const user = users.find(u => u.username === username);

  if (!user) {
    return res.status(401).json({ message: 'Invalid username or password' });
  }

  const isPasswordValid = await bcrypt.compare(password, user.password);
  if (!isPasswordValid) {
    return res.status(401).json({ message: 'Invalid username or password' });
  }

  const token = jwt.sign({ userId: user.id, username: user.username }, secretKey, { expiresIn: '1h' });
  res.json({ token });
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
