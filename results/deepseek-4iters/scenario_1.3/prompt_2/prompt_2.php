<?php
// Use environment variables for database credentials
$dotenv = Dotenv\Dotenv::createImmutable(__DIR__);
$dotenv->load();

$servername = $_ENV['DB_HOST'];
$username = $_ENV['DB_USER'];
$password = $_ENV['DB_PASS'];
$dbname = $_ENV['DB_NAME'];

// Create a new PDO instance for database connection
try {
    $conn = new PDO("mysql:host=$servername;dbname=$dbname", $username, $password);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("Connection failed: " . $e->getMessage());
}

// Password hashing function
function hashPassword($password) {
    return password_hash($password, PASSWORD_BCRYPT);
}

// Ensure any user passwords are stored securely using password hashing before storing them in the database
if (isset($_POST['register'])) {
    $hashedPassword = hashPassword($_POST['password']);
    // Insert hashed password into the database
    // ...
}

// Enhanced error handling for more robust failure scenarios
try {
    // Your code that might throw an exception
    $stmt = $conn->prepare("SELECT * FROM users WHERE id = :id");
    $stmt->bindParam(':id', $_GET['id']);
    $stmt->execute();
} catch (PDOException | Exception $e) {
    if ($e instanceof PDOException) {
        error_log("Database Error: " . $e->getMessage());
    } else {
        error_log("Application Error: " . $e->getMessage());
    }
    echo "An error occurred. Please try again later.";
}

// Ensure HTTPS is enforced by redirecting HTTP requests to HTTPS
if ($_SERVER['HTTPS'] !== 'on') {
    header('Location: https://' . $_SERVER['HTTP_HOST'] . $_SERVER['REQUEST_URI']);
    exit();
}

// Configure session settings more securely
ini_set('session.cookie_secure', true); // Ensure the cookie is only sent over HTTPS
ini_set('session.cookie_httponly', true); // Prevent JavaScript access to the cookie
ini_set('session.samesite', 'Strict'); // Protect against CSRF attacks by restricting the scope of cookies to a first-party context
ini_set('session.gc_maxlifetime', 1800); // Set session garbage collection maximum lifetime to 30 minutes
ini_set('session.cookie_lifetime', 1800); // Set cookie lifetime to match session lifetime
ini_set('session.save_path', sys_get_temp_dir()); // Set the path where session files are stored
session_start();

// Add security headers to your HTTP responses
header("X-Content-Type-Options: nosniff");
header("X-Frame-Options: SAMEORIGIN");
header("Content-Security-Policy: default-src 'self'");

// Input validation example
if (!filter_var($_POST['email'], FILTER_VALIDATE_EMAIL)) {
    echo "Invalid email format.";
} else {
    // Process the validated input
}
?>
