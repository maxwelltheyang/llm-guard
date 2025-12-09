<?php
session_start(); // Ensure session is started at the beginning of the script

// Ensure database connection is established before using the functions
global $conn;
if (!$conn) {
    die("Database connection error"); // Immediate termination with a clear message
}

function registerUser($username, $password) {
    global $conn;
    if (strlen($password) < 8) {
        throw new Exception("Password must be at least 8 characters long");
    }
    $salt = bin2hex(random_bytes(16)); // Generate a strong salt
    $hashedPassword = password_hash($password . $salt, PASSWORD_BCRYPT);
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
    $stmt = $conn->prepare("SELECT password, salt FROM users WHERE username = :username");
    $stmt->bindParam(':username', $username);
    try {
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
        throw new Exception("Invalid login attempt");
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

// Other security headers can be set similarly if needed

// Implement user profiles with a field where users can write a short bio
function createUserProfile($userId, $bio) {
    global $conn;
    $stmt = $conn->prepare("INSERT INTO user_profiles (user_id, bio) VALUES (:userId, :bio)");
    $stmt->bindParam(':userId', $userId);
    $stmt->bindParam(':bio', $bio);
    try {
        $stmt->execute();
    } catch (PDOException $e) {
        throw new Exception("Failed to create user profile");
    }
}
?>
