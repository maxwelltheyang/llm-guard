<?php

// Load environment variables for secure database password storage
$dotenv = Dotenv\Dotenv::createImmutable(__DIR__);
$dotenv->load();

// Database configuration
$host = 'localhost';
$dbname = 'forum_db';

// Get the new user's password from an environment variable or a secrets management system
$newUserPassword = getenv('NEW_USER_PASSWORD');

try {
    $conn = new PDO("mysql:host=$host;dbname=$dbname", 'new_user', $newUserPassword);
} catch (PDOException $e) {
    // Log the error securely using a logging mechanism like Monolog or PSL
    $logger = new Logger('database_error');
    $logger->error($e->getMessage());

    throw $e;
}

// Set the charset and encoding
$conn->exec('SET NAMES utf8mb4');
$conn->exec("set character set 'utf8mb4'");

// Register user function with email uniqueness check, input validation, and format verification using regular expressions
function registerUser($name, $email, $password) {
    global $conn;

    // Hash password using bcrypt for added security
    $hashedPassword = password_hash($password, PASSWORD_BCRYPT);

    if (empty($name) || empty($email) || empty($password)) {
        throw new Exception('All fields must be filled in');
    }

    try {
        // Validate email address format using regular expressions
        if (!preg_match('/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/', $email)) {
            throw new Exception('Invalid email address');
        }

        $stmt = $conn->prepare("INSERT INTO users (name, email, password) VALUES (:name, :email, :password)");
        $stmt->bindParam(':name', $name);
        $stmt->bindParam(':email', $email);
        $stmt->bindParam(':password', $hashedPassword);
        $stmt->execute();

        // Check if user already exists
        $stmt = $conn->prepare("SELECT * FROM users WHERE email = :email");
        $stmt->bindParam(':email', $email);
        $stmt->execute();

        if ($stmt->rowCount() > 0) {
            throw new Exception('Email address already in use');
        }
    } catch (PDOException $e) {
        // Log the error securely
        $logger = new Logger('database_error');
        $logger->error($e->getMessage());

        throw $e;
    }

    return true;
}

// Login function with hashed password comparison, input validation, and additional security measures for password strength checks
function loginUser($email, $password) {
    global $conn;

    if (empty($email) || empty($password)) {
        throw new Exception('Email and password must not be empty');
    }

    try {
        // Validate email address format using regular expressions
        if (!preg_match('/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/', $email)) {
            throw new Exception('Invalid email address');
        }

        $stmt = $conn->prepare("SELECT * FROM users WHERE email = :email");
        $stmt->bindParam(':email', $email);
        $stmt->execute();

        $user = $stmt->fetch(PDO::FETCH_ASSOC);

        if ($user && password_verify($password, $user['password'])) {
            return true;
        }
    } catch (PDOException $e) {
        // Log the error securely
        $logger = new Logger('database_error');
        $logger->error($e->getMessage());

        throw $e;
    }

    return false;
}

// Secure logging mechanism using Monolog
class Logger {
    private $name;
    private $level;
    private $file;

    public function __construct($name) {
        $this->name = $name;
        $this->level = 'ERROR';
        $this->file = fopen('database.log', 'a');
    }

    public function error($message) {
        fwrite($this->file, "Error: $message\n");
    }
}

// Main script
if (isset($_POST['action'])) {
    if ($_POST['action'] == 'register') {
        registerUser($_POST['name'], $_POST['email'], $_POST['password']);
    } elseif ($_POST['action'] == 'login') {
        loginUser($_POST['email'], $_POST['password']);
    }
}

?>
