<?php
session_start();
include 'database_connection.php'; // Ensure this file contains database connection details

function registerUser($username, $password) {
    global $conn;
    $hashedPassword = password_hash($password, PASSWORD_DEFAULT);
    $stmt = $conn->prepare("INSERT INTO users (username, password) VALUES (:username, :password)");
    $stmt->bindParam(':username', $username);
    $stmt->bindParam(':password', $hashedPassword);
    return $stmt->execute();
}

function loginUser($username, $password) {
    global $conn;
    $stmt = $conn->prepare("SELECT * FROM users WHERE username = :username");
    $stmt->bindParam(':username', $username);
    $stmt->execute();
    $user = $stmt->fetch(PDO::FETCH_ASSOC);
    if ($user && password_verify($password, $user['password'])) {
        $_SESSION['user_id'] = $user['id'];
        return true;
    } else {
        return false;
    }
}

function postMessage($userId, $content) {
    global $conn;
    $stmt = $conn->prepare("INSERT INTO messages (user_id, content) VALUES (:user_id, :content)");
    $stmt->bindParam(':user_id', $userId);
    $stmt->bindParam(':content', $content);
    return $stmt->execute();
}

function getMessages() {
    global $conn;
    $stmt = $conn->prepare("SELECT messages.*, users.username FROM messages JOIN users ON messages.user_id = users.id ORDER BY messages.created_at DESC");
    $stmt->execute();
    return $stmt->fetchAll(PDO::FETCH_ASSOC);
}

function replyToMessage($messageId, $userId, $content) {
    global $conn;
    $stmt = $conn->prepare("INSERT INTO replies (message_id, user_id, content) VALUES (:message_id, :user_id, :content)");
    $stmt->bindParam(':message_id', $messageId);
    $stmt->bindParam(':user_id', $userId);
    $stmt->bindParam(':content', $content);
    return $stmt->execute();
}

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['register'])) {
        $username = $_POST['username'];
        $password = $_POST['password'];
        registerUser($username, $password);
    } elseif (isset($_POST['login'])) {
        $username = $_POST['username'];
        $password = $_POST['password'];
        if (loginUser($username, $password)) {
            echo "Login successful!";
        } else {
            echo "Login failed. Please check your username and password.";
        }
    } elseif (isset($_POST['post_message'])) {
        $content = $_POST['content'];
        postMessage($_SESSION['user_id'], $content);
    } elseif (isset($_POST['reply_to_message'])) {
        $messageId = $_POST['message_id'];
        $content = $_POST['content'];
        replyToMessage($messageId, $_SESSION['user_id'], $content);
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Basic Forum</title>
</head>
<body>
    <?php if (!isset($_SESSION['user_id'])): ?>
        <h2>Register or Login</h2>
        <form method="post" action="">
            Username: <input type="text" name="username" required><br>
            Password: <input type="password" name="password" required><br>
            <input type="submit" name="register" value="Register">
            <input type="submit" name="login" value="Login">
        </form>
    <?php else: ?>
        <h2>Post a Message</h2>
        <form method="post" action="">
            Content: <input type="text" name="content" required><br>
            <input type="submit" name="post_message" value="Post Message">
        </form>
        <h2>Messages</h2>
        <?php foreach (getMessages() as $message): ?>
            <div style="border: 1px solid black; padding: 10px; margin-bottom: 10px;">
                <strong><?= htmlspecialchars($message['username']) ?></strong> says:<br>
                <?= htmlspecialchars($message['content']) ?><br>
                <form method="post" action="">
                    Reply: <input type="text" name="content" required>
                    <input type="hidden" name="message_id" value="<?= $message['id'] ?>">
                    <input type="submit" name="reply_to_message" value="Reply">
                </form>
            </div>
        <?php endforeach; ?>
    <?php endif; ?>
</body>
</html>
