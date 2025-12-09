<?php
session_start(); // Start session at the beginning of the script

// Ensure database connection is established before using the functions
global $conn;
if (!$conn) {
    error_log("Database connection failed"); // Log the error for debugging purposes
    die("Database connection error");
}

function registerUser($username, $password) {
    global $conn;
    if (strlen($password) < 8) {
        throw new Exception("Password must be at least 8 characters long");
    }
    $salt = bin2hex(random_bytes(16)); // Generate a strong salt
    $hashedPassword = password_hash($password . $salt, PASSWORD_BCRYPT);
    try {
        $stmt = $conn->prepare("INSERT INTO users (username, password, salt) VALUES (:username, :password, :salt)");
        $stmt->bindParam(':username', $username);
        $stmt->bindParam(':password', $hashedPassword);
        $stmt->bindParam(':salt', $salt);
        $stmt->execute();
    } catch (PDOException $e) {
        throw new Exception("Failed to register user: " . $e->getMessage());
    }
}

function loginUser($username, $password) {
    global $conn;
    try {
        $stmt = $conn->prepare("SELECT password, salt FROM users WHERE username = :username");
        $stmt->bindParam(':username', $username);
        $stmt->execute();
        $result = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($result && password_verify($password . $result['salt'], $result['password'])) {
            session_start(); // Start or resume a session
            $_SESSION['username'] = $username;
            return true;
        } else {
            throw new Exception("Invalid username or password");
        }
    } catch (Exception $e) {
        throw new Exception("Invalid login attempt: " . $e->getMessage());
    }
}

function sanitizeInput($input) {
    // Add more robust validation if necessary, but for now, just trim and return
    return trim($input);
}

// Set a more secure default-src in the CSP
$csp = "default-src 'self'; script-src 'self' https://apis.example.com; style-src 'self' https://fonts.googleapis.com";
if (!headers_sent()) {
    header("Content-Security-Policy: $csp");
}

function createUserProfile($userId) {
    global $conn;
    try {
        $stmt = $conn->prepare("SELECT * FROM users WHERE id = :id");
        $stmt->bindParam(':id', $userId);
        $stmt->execute();
        $user = $stmt->fetch(PDO::FETCH_ASSOC);
        if ($user) {
            // Create user profile logic here
            return $user;
        } else {
            throw new Exception("User not found");
        }
    } catch (Exception $e) {
        throw new Exception("Failed to create user profile: " . $e->getMessage());
    }
}

// Example usage of sanitizeInput and other functions
try {
    // Sanitize input before using it in a query
    $sanitizedUsername = sanitizeInput($_POST['username']);

    // Register a new user
    registerUser($sanitizedUsername, $_POST['password']);

    // Log in the user
    loginUser($sanitizedUsername, $_POST['password']);

    // Create user profile for the logged-in user
    if (isset($_SESSION['username'])) {
        $userProfile = createUserProfile(1); // Assuming userId is 1 for this example
        echo "Welcome, " . htmlspecialchars($userProfile['username']) . "!";
    }
} catch (Exception $e) {
    die("Error: " . $e->getMessage());
}
?>
