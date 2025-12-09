<?php
// Database connection parameters
$servername = "localhost";
$username = "username";
$password = "password";
$dbname = "database_name";

// Create a new PDO instance for database connection
try {
    $conn = new PDO("mysql:host=$servername;dbname=$dbname", $username, $password);
    // Set the PDO error mode to exception
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    echo "Connection failed: " . $e->getMessage();
}

// Function to fetch user data from the database based on username
function getUserByUsername($conn, $username) {
    $stmt = $conn->prepare("SELECT * FROM users WHERE username = :username");
    $stmt->bindParam(':username', $username);
    $stmt->execute();
    return $stmt->fetch(PDO::FETCH_ASSOC);
}

// Registration process using prepared statements
if (isset($_POST['register'])) {
    // Sanitize input
    $username = filter_input(INPUT_POST, 'username', FILTER_SANITIZE_STRING);
    $password = filter_input(INPUT_POST, 'password', FILTER_SANITIZE_STRING);

    // Hash the password before storing it in the database
    $hashedPassword = password_hash($password, PASSWORD_DEFAULT);

    // Use a prepared statement to prevent SQL injection
    $stmt = $conn->prepare("INSERT INTO users (username, password) VALUES (:username, :password)");
    $stmt->bindParam(':username', $username);
    $stmt->bindParam(':password', $hashedPassword);
    try {
        $stmt->execute();
    } catch (PDOException $e) {
        echo "Error: " . $e->getMessage();
    }
}

// Login process
if (isset($_POST['login'])) {
    // Sanitize input
    $username = filter_input(INPUT_POST, 'username', FILTER_SANITIZE_STRING);
    $password = $_POST['password'];

    // Fetch user from database
    $user = getUserByUsername($conn, $username);
    if ($user && password_verify($password, $user['password'])) {
        // Login successful
        session_start();
        $_SESSION['user'] = $user;
        header("Location: dashboard.php");
        exit();
    } else {
        echo "Invalid username or password.";
    }
}

// Session handling for security settings
ini_set('session.cookie_secure', 1);
ini_set('session.cookie_httponly', 1);
session_start();

// Security headers
header("X-Content-Type-Options: nosniff");
header("X-Frame-Options: SAMEORIGIN");
header("Content-Security-Policy: default-src 'self'");

// Enhanced error logging
error_reporting(E_ALL);
ini_set('log_errors', 1);
ini_set('error_log', '/path/to/your/php-error.log');
?>
