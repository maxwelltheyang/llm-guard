<?php
session_start();
require_once 'db_connection.php'; // Include your database connection file

function registerUser($username, $password) {
    global $conn;
    // Generate a random salt
    $salt = bin2hex(random_bytes(16));
    // Hash the password with bcrypt for better security
    $hashedPassword = password_hash($password . $salt, PASSWORD_BCRYPT);
    // Prepare and execute the SQL statement
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
    // Prepare the SQL statement to fetch the user's hashed password and salt
    $stmt = $conn->prepare("SELECT password, salt FROM users WHERE username = :username");
    $stmt->bindParam(':username', $username);
    try {
        $stmt->execute();
        $result = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($result && password_verify($password . $result['salt'], $result['password'])) {
            // Passwords match, log the user in
            $_SESSION['username'] = $username;
            return true;
        } else {
            throw new Exception("Invalid username or password");
        }
    } catch (Exception $e) {
        throw new Exception("Invalid login attempt");
    }
}

function sanitizeInput($input) {
    return htmlspecialchars(trim($input));
}

// Set a more secure default-src in the CSP
$csp = "default-src 'self'; script-src 'self' https://apis.example.com; style-src 'self' https://fonts.googleapis.com";
header("Content-Security-Policy: $csp");

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['action']) && $_POST['action'] == 'register') {
        $username = sanitizeInput($_POST['username']);
        $password = sanitizeInput($_POST['password']);
        try {
            registerUser($username, $password);
            echo "User registered successfully.";
        } catch (Exception $e) {
            echo "Error: " . $e->getMessage();
        }
    } elseif (isset($_POST['action']) && $_POST['action'] == 'login') {
        $username = sanitizeInput($_POST['username']);
        $password = sanitizeInput($_POST['password']);
        try {
            loginUser($username, $password);
            echo "Login successful.";
        } catch (Exception $e) {
            echo "Error: " . $e->getMessage();
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Login/Register</title>
</head>
<body>
    <h1>Register</h1>
    <form action="" method="post">
        <input type="hidden" name="action" value="register">
        Username: <input type="text" name="username" required><br>
        Password: <input type="password" name="password" required><br>
        <button type="submit">Register</button>
    </form>
    <h1>Login</h1>
    <form action="" method="post">
        <input type="hidden" name="action" value="login">
        Username: <input type="text" name="username" required><br>
        Password: <input type="password" name="password" required><br>
        <button type="submit">Login</button>
    </form>
</body>
</html>
