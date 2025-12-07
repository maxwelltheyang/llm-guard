const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');

const secretKey = 'mysecretkey';

function generateToken(user, password) {
  const hashedPassword = bcrypt.hashSync(password, 10);
  if (hashedPassword === user.password) {
    const token = jwt.sign({ username: user.username }, secretKey, { expiresIn: '1h' });
    return token;
  } else {
    return null;
  }
}

function verifyToken(token) {
  try {
    const decoded = jwt.verify(token, secretKey);
    return true;
  } catch (err) {
    return false;
  }
}

const user = { username: 'testuser', password: bcrypt.hashSync('testpassword', 10) };

console.log(generateToken(user, 'testpassword')); // This should print a JWT token
console.log(verifyToken('JWT token from generateToken')); // This should print true or false depending on whether the token is valid
