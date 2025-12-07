const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');

const users = [
  { id: 1, username: 'user1', passwordHash: '$2b$10$fVH8e28OQRj9tQI3SS0muuJ8Nx7D/t1k6YAiourCgrz9dC6J/IEsa' }
];

const secretKey = 'your_secret_key';

async function login(username, password) {
  const user = users.find(u => u.username === username);
  if (!user) {
    throw new Error('Invalid credentials');
  }

  const passwordMatch = await bcrypt.compare(password, user.passwordHash);
  if (!passwordMatch) {
    throw new Error('Invalid credentials');
  }

  const token = jwt.sign({ id: user.id, username: user.username }, secretKey, { expiresIn: '1h' });
  return token;
}

module.exports = login;
