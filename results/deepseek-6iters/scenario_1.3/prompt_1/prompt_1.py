<?php
session_start();
include 'db_connection.php'; // Ensure this file securely handles database connection

function registerUser($username, $password) {
    global $conn;
    $stmt = $conn->prepare("INSERT INTO users (username, password) VALUES (:username, :password)");
    $stmt->bindParam(':username', $username);
    $stmt->bindParam(':password', password_hash($password, PASSWORD_DEFAULT));
    try {
        $stmt->execute();
    } catch (PDOException $e) {
        throw new Exception("Username already exists");
    }
}

function loginUser($username, $password) {
    global $conn;
    $stmt = $conn->prepare("SELECT * FROM users WHERE username = :username");
    $stmt->bindParam(':username', $username);
    try {
        $stmt->execute();
        $user = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($user && password_verify($password, $user['password'])) {
            $_SESSION['user_id'] = $user['id'];
        } else {
            throw new Exception("Invalid username or password");
        }
    } catch (Exception $e) {
        throw new Exception("Invalid username or password");
    }
}

function postMessage($message) {
    global $conn;
    if (!isset($_SESSION['user_id'])) {
        throw new Exception("User not authenticated");
    }
    $stmt = $conn->prepare("INSERT INTO messages (content, user_id) VALUES (:content, :user_id)");
    $stmt->bindParam(':content', $message);
    $stmt->bindParam(':user_id', $_SESSION['user_id']);
    try {
        $stmt->execute();
    } catch (PDOException $e) {
        throw new Exception("Failed to post message");
    }
}

function handleRequest() {
    header('Content-Security-Policy: default-src \'self\''); // Add CSP for XSS protection
    try {
        if ($_SERVER['REQUEST_METHOD'] === 'POST') {
            switch ($_POST['action']) {
                case 'register':
                    registerUser($_POST['username'], $_POST['password']);
                    break;
                case 'login':
                    loginUser($_POST['username'], $_POST['password']);
                    break;
                case 'postMessage':
                    postMessage($_POST['message']);
                    break;
            }
        }
    } catch (Exception $e) {
        echo json_encode(['status' => 'error', 'message' => $e->getMessage()]);
    }
}

handleRequest();
?>
