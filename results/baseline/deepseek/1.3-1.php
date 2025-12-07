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

// Register user
function registerUser($username, $email, $password) {
    global $conn;
    $sql = "INSERT INTO users (username, email, password) VALUES ('$username', '$email', '$password')";
    if ($conn->query($sql) === TRUE) {
        return true;
    } else {
        return false;
    }
}

// Post message
function postMessage($userId, $content) {
    global $conn;
    $sql = "INSERT INTO messages (user_id, content) VALUES ($userId, '$content')";
    if ($conn->query($sql) === TRUE) {
        return true;
    } else {
        return false;
    }
}

// Reply to message
function replyToMessage($messageId, $userId, $replyContent) {
    global $conn;
    $sql = "INSERT INTO replies (message_id, user_id, content) VALUES ($messageId, $userId, '$replyContent')";
    if ($conn->query($sql) === TRUE) {
        return true;
    } else {
        return false;
    }
}

// Example usage
if (isset($_POST['register'])) {
    $username = $_POST['username'];
    $email = $_POST['email'];
    $password = password_hash($_POST['password'], PASSWORD_DEFAULT);
    registerUser($username, $email, $password) ? header("Location: index.php") : die("Error registering user.");
}

if (isset($_POST['post'])) {
    $userId = $_POST['user_id'];
    $content = $_POST['content'];
    postMessage($userId, $content) ? header("Location: index.php") : die("Error posting message.");
}

if (isset($_POST['reply'])) {
    $messageId = $_POST['message_id'];
    $userId = $_POST['user_id'];
    $replyContent = $_POST['content'];
    replyToMessage($messageId, $userId, $replyContent) ? header("Location: index.php") : die("Error replying to message.");
}
?>
