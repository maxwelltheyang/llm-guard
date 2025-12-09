<?php
// Ensure database connection is established before using the functions
global $conn;
if (!$conn) {
    // Establish database connection here
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
if (!headers_sent()) {
    header("Content-Security-Policy: $csp");
}

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['action']) && $_POST['action'] == 'register') {
        try {
            $username = sanitizeInput($_POST['username']);
            $password = sanitizeInput($_POST['password']);
            registerUser($username, $password);
            echo "Registration successful";
        } catch (Exception $e) {
            echo "Registration failed: " . $e->getMessage();
        }
    } elseif (isset($_POST['action']) && $_POST['action'] == 'login') {
        try {
            $username = sanitizeInput($_POST['username']);
            $password = sanitizeInput($_POST['password']);
            if (loginUser($username, $password)) {
                echo "Login successful";
            } else {
                echo "Invalid username or password";
            }
        } catch (Exception $e) {
            echo "Login failed: " . $e->getMessage();
        }
    }
}
?>
