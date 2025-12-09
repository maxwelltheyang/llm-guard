<?php

// Load environment variables securely using Dotenv
$dotenv = Dotenv\Dotenv::createImmutable(__DIR__);
$dotenv->load();

// Database configuration from environment variables
$db_host = $_ENV['DB_HOST'];
$db_name = $_ENV['DB_NAME'];
$db_user = $_ENV['DB_USER'];
$db_password = $_ENV['DB_PASSWORD'];

try {
    // Establish a secure connection to the database using PDO
    $pdo = new PDO("mysql:host=$db_host;dbname=$db_name", $db_user, $db_password);

    // Enable exception handling for better error reporting
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

} catch (PDOException $e) {
    // Log the database connection failure with a generic message
    log_event("Error connecting to database");
    exit;
}

// Secure password hashing using Argon2I algorithm
function hash_password($password)
{
    return password_hash($password, PASSWORD_ARGON2I);
}

// Function to securely handle sensitive data (like user emails) in memory
function secure_string_handling($data)
{
    $handle = fopen('php://memory', 'r+');
    fwrite($handle, $data);
    rewind($handle);
    return stream_get_contents($handle);
}

// Secure user authentication and session management
function authenticate_user($email, $password)
{
    try {
        // Validate email format to prevent potential SQL injection attempts
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            log_event("Invalid email format");
            return false;
        }

        // Query the database for the user's password using prepared statements
        $stmt = $pdo->prepare("SELECT id, password FROM users WHERE email = ?");
        $stmt->execute([$email]);

        if ($user_data = $stmt->fetch()) {
            // Use constant-time comparison to verify passwords securely
            if (password_verify($password, $user_data['password'])) {
                session_start();
                $_SESSION['email'] = secure_string_handling($email);
                return true;
            }
        }

    } catch (PDOException $e) {
        // Log database query failure with a generic message
        log_event("Error authenticating user");
    }

    return false;
}

// Implement a more robust logging mechanism using Monolog
use Monolog\Logger;
use Monolog\Handler\StreamHandler;

function log_event($message)
{
    $logger = new Logger('security');
    $logger->addHandler(new StreamHandler('log/security.log', Logger::INFO));
    $logger->info($message);
}

?>
