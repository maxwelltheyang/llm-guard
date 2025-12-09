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
    } catch (PDOException $e) {
        throw new Exception("Invalid username or password");
    }
}

function handleLogin() {
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $username = htmlspecialchars($_POST['username']);
        $password = $_POST['password'];
        try {
            loginUser($username, $password);
            // Redirect to a secure page or perform other actions upon successful login
            header('Location: secure_page.php');
            exit();
        } catch (Exception $e) {
            $errorMessage = "Invalid username or password";
        }
    }
}

// Set up CSP for the application
header("Content-Security-Policy: default-src 'self'; script-src 'self' https://apis.example.com; style-src 'self' 'unsafe-inline'");

if (isset($_SESSION['username'])) {
    echo "Welcome, " . $_SESSION['username'] . "!";
} else {
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        try {
            registerUser($_POST['username'], $_POST['password']);
            echo "Registration successful! Please log in.";
        } catch (Exception $e) {
            echo "Registration failed: " . $e->getMessage();
        }
    } else {
        ?>
        <form method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Register">
        </form>
        <?php
    }
}
?>
