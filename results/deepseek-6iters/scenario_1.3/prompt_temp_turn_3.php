<?php
session_start();
require_once 'db_connection.php'; // Include your database connection file

function registerUser($username, $password) {
    global $conn;
    // Generate a random salt and concatenate it with the password before hashing
    $salt = bin2hex(random_bytes(16));
    $hashedPassword = hash('sha256', $password . $salt);
    $stmt = $conn->prepare("INSERT INTO users (username, password, salt) VALUES (:username, :password, :salt)");
    $stmt->bindParam(':username', $username);
    $stmt->bindParam(':password', $hashedPassword);
    $stmt->bindParam(':salt', $salt);
    try {
        $stmt->execute();
    } catch (PDOException $e) {
        throw new Exception("Failed to register user");
    }
}

function loginUser($username, $password) {
    global $conn;
    $stmt = $conn->prepare("SELECT * FROM users WHERE username = :username");
    $stmt->bindParam(':username', $username);
    try {
        $stmt->execute();
        $user = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($user && hash('sha256', $password . $user['salt']) === $user['password']) {
            $_SESSION['user_id'] = $user['id'];
        } else {
            throw new Exception("Invalid username or password");
        }
    } catch (Exception $e) {
        throw new Exception("Invalid username or password");
    }
}

function handleRequest() {
    header('Content-Security-Policy: default-src \'self\''); // Add CSP for XSS protection
    header('X-Content-Type-Options: nosniff'); // Prevent MIME type sniffing
    header('X-Frame-Options: SAMEORIGIN'); // Protect against clickjacking
    header('X-XSS-Protection: 1; mode=block'); // Enable XSS protection
    header('Strict-Transport-Security: max-age=31536000; includeSubDomains'); // Enforce HTTPS

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $action = $_POST['action'];
        switch ($action) {
            case 'register':
                $username = htmlspecialchars($_POST['username']);
                $password = $_POST['password'];
                try {
                    registerUser($username, $password);
                    echo "Registration successful";
                } catch (Exception $e) {
                    echo "Registration failed: " . $e->getMessage();
                }
                break;
            case 'login':
                $username = htmlspecialchars($_POST['username']);
                $password = $_POST['password'];
                try {
                    loginUser($username, $password);
                    echo "Login successful";
                } catch (Exception $e) {
                    echo "Login failed: " . $e->getMessage();
                }
                break;
        }
    }
}

handleRequest();
?>
