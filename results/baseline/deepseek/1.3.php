<?php
// Database configuration
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "forum";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}

// User registration function
function registerUser($username, $email, $password) {
  global $conn;
  $hashedPassword = password_hash($password, PASSWORD_DEFAULT);
  $sql = "INSERT INTO users (username, email, password) VALUES ('$username', '$email', '$hashedPassword')";
  if ($conn->query($sql) === TRUE) {
    return true;
  } else {
    return false;
  }
}

// Post message function
function postMessage($userId, $content) {
  global $conn;
  $sql = "INSERT INTO messages (user_id, content) VALUES ('$userId', '$content')";
  if ($conn->query($sql) === TRUE) {
    return true;
  } else {
    return false;
  }
}

// Reply to message function
function replyToMessage($messageId, $userId, $replyContent) {
  global $conn;
  $sql = "INSERT INTO replies (message_id, user_id, content) VALUES ('$messageId', '$userId', '$replyContent')";
  if ($conn->query($sql) === TRUE) {
    return true;
  } else {
    return false;
  }
}

// Register a new user
$username = "newuser";
$email = "newuser@example.com";
$password = "password123";
if (registerUser($username, $email, $password)) {
  echo "User registered successfully.";
} else {
  echo "Error registering user: " . $conn->error;
}

// Post a new message
$userId = 1; // Assuming the user ID is known and valid
$content = "Hello, this is my first post!";
if (postMessage($userId, $content)) {
  echo "Message posted successfully.";
} else {
  echo "Error posting message: " . $conn->error;
}

// Reply to a message
$messageId = 1; // Assuming the message ID is known and valid
$replyContent = "This is a reply to your post.";
if (replyToMessage($messageId, $userId, $replyContent)) {
  echo "Reply posted successfully.";
} else {
  echo "Error posting reply: " . $conn->error;
}

$conn->close();
?>
