const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

const app = express();
app.use(express.json());

// Secret key for signing the JWT
const secretKey = 'mysecretkey';

// User model (simple example)
class User {
  constructor(username, password) {
    this.username = username;
    this.passwordHash = bcrypt.hashSync(password, 10);
  }
}

let users = [
  new User('user1', 'password1'),
  new User('user2', 'password2')
];

// Login function
async function login(req, res) {
  const { username, password } = req.body;

  // Find the user with the given username
  let user = users.find(u => u.username === username);

  if (!user) {
    return res.status(401).send({ error: 'Invalid username or password' });
  }

  // Compare passwords using bcrypt
  const isValidPassword = await bcrypt.compare(password, user.passwordHash);

  if (!isValidPassword) {
    return res.status(401).send({ error: 'Invalid username or password' });
  }

  // Issue JWT upon successful login
  const token = jwt.sign({
    username,
    exp: Math.floor(Date.now() / 1000) + (60 * 30) // expires in 30 minutes
  }, secretKey);

  res.json({ token });
}

// Route for login
app.post('/login', login);

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
