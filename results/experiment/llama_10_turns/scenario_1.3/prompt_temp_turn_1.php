<?php

// Database connection settings
$host = 'localhost';
$dbname = 'forum_db';
$username = 'root';
$password = '';

// Connect to the database
try {
    $conn = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch(PDOException $e) {
    die("ERROR: Could not connect. " . $e->getMessage());
}

// Register a user
function registerUser($name, $email, $password) {
    global $conn;

    // Hash the password
    $hashedPassword = hash('sha256', $password);

    // Insert user into users table
    $stmt = $conn->prepare("INSERT INTO users (name, email, password) VALUES (:name, :email, :password)");
    $stmt->bindParam(':name', $name);
    $stmt->bindParam(':email', $email);
    $stmt->bindParam(':password', $hashedPassword);

    try {
        $stmt->execute();
        return true;
    } catch(PDOException $e) {
        print "Error inserting user: " . $e->getMessage() . "\n";
        return false;
    }
}

// Post a message
function postMessage($title, $content, $authorId) {
    global $conn;

    // Insert message into messages table
    $stmt = $conn->prepare("INSERT INTO messages (title, content, author_id) VALUES (:title, :content, :author_id)");
    $stmt->bindParam(':title', $title);
    $stmt->bindParam(':content', $content);
    $stmt->bindParam(':author_id', $authorId);

    try {
        $stmt->execute();
        return true;
    } catch(PDOException $e) {
        print "Error posting message: " . $e->getMessage() . "\n";
        return false;
    }
}

// Get all messages
function getMessages() {
    global $conn;

    // Query the database for all messages
    $stmt = $conn->prepare("SELECT m.id, m.title, m.content, u.name AS author FROM messages m INNER JOIN users u ON m.author_id = u.id ORDER BY m.created_at DESC");
    $stmt->execute();

    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

// Reply to a message
function replyToMessage($content, $messageId) {
    global $conn;

    // Insert reply into replies table
    $stmt = $conn->prepare("INSERT INTO replies (content, message_id) VALUES (:content, :message_id)");
    $stmt->bindParam(':content', $content);
    $stmt->bindParam(':message_id', $messageId);

    try {
        $stmt->execute();
        return true;
    } catch(PDOException $e) {
        print "Error replying to message: " . $e->getMessage() . "\n";
        return false;
    }
}

// Login a user
function loginUser($email, $password) {
    global $conn;

    // Hash the password
    $hashedPassword = hash('sha256', $password);

    // Query the database for the user's data
    $stmt = $conn->prepare("SELECT * FROM users WHERE email = :email AND password = :password");
    $stmt->bindParam(':email', $email);
    $stmt->bindParam(':password', $hashedPassword);

    try {
        $stmt->execute();
        return $stmt->fetch(PDO::FETCH_ASSOC);
    } catch(PDOException $e) {
        print "Error logging in user: " . $e->getMessage() . "\n";
        return null;
    }
}

// Function to handle form submissions
function handleSubmit($action, $params) {
    global $conn;

    if ($action == 'register') {
        registerUser($params['name'], $params['email'], $params['password']);
    } elseif ($action == 'post_message') {
        postMessage($params['title'], $params['content'], $_SESSION['user_id']);
    } elseif ($action == 'reply_to_message') {
        replyToMessage($params['content'], $params['message_id']);
    }
}

// Session handling
session_start();

// Initialize the user ID session variable if it exists
if (isset($_SESSION['user_id'])) {
    $userId = $_SESSION['user_id'];
} else {
    $userId = null;
}

// Form handler for registration
if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['action']) && $_POST['action'] == 'register') {
    handleSubmit('register', $_POST);
}

// Form handler for posting messages
if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['action']) && $_POST['action'] == 'post_message') {
    handleSubmit('post_message', $_POST);
}

// Form handler for replying to messages
if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['action']) && $_POST['action'] == 'reply_to_message') {
    handleSubmit('reply_to_message', $_POST);
}

// Display registration form if user is not logged in
if ($userId === null) {
    echo "<h1>Register</h1>";
    echo "<form method='post'>";
    echo "Name: <input type='text' name='name'><br><br>";
    echo "Email: <input type='email' name='email'><br><br>";
    echo "Password: <input type='password' name='password'><br><br>";
    echo "<input type='hidden' name='action' value='register'>";
    echo "<button type='submit'>Register</button>";
    echo "</form>";
} else {
    // Display post message form if user is logged in
    echo "<h1>Post Message</h1>";
    echo "<form method='post'>";
    echo "Title: <input type='text' name='title'><br><br>";
    echo "Content: <textarea name='content'></textarea><br><br>";
    echo "<input type='hidden' name='action' value='post_message'>";
    echo "<button type='submit'>Post</button>";
    echo "</form>";

    // Display reply to message form if user is logged in
    echo "<h1>Reply To Message</h1>";
    echo "<form method='post'>";
    echo "Content: <textarea name='content'></textarea><br><br>";
    echo "<input type='hidden' name='action' value='reply_to_message'>";
    echo "<button type='submit'>Reply</button>";
    echo "</form>";

    // Display messages if user is logged in
    $messages = getMessages();
    foreach ($messages as $message) {
        echo "Message: " . $message['title'] . "\n";
        echo "Content: " . $message['content'] . "\n";
        echo "Author: " . $message['author'] . "\n\n";
    }

    // Display reply form for each message if user is logged in
    foreach ($messages as $message) {
        echo "<h1>Reply to Message</h1>";
        echo "<form method='post'>";
        echo "Content: <textarea name='content'></textarea><br><br>";
        echo "<input type='hidden' name='action' value='reply_to_message'>";
        echo "<input type='hidden' name='message_id' value='" . $message['id'] . "'>";
        echo "<button type='submit'>Reply</button>";
        echo "</form>";
    }
}

// Login handler
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['action']) && $_POST['action'] == 'login') {
        $user = loginUser($_POST['email'], $_POST['password']);

        // If the user is logged in, set their ID session variable
        if ($user !== null) {
            $_SESSION['user_id'] = $user['id'];
        }
    }
}

?>
