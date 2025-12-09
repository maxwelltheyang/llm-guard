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

    // Enable error reporting on database queries for better error handling
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_WARNINGS);

} catch (PDOException $e) {
    // Log specific database connection failure details with the corresponding error code
    log_event("Error connecting to database: " . $e->getCode() . " - " . $e->getMessage());
    exit;
}

// Function to get user profile information
function getUserProfile($userId)
{
    try {
        $stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id");
        $stmt->bindParam(':id', $userId);
        $stmt->execute();

        return $stmt->fetch(PDO::FETCH_ASSOC);

    } catch (PDOException $e) {
        // Log specific database query failure details with the corresponding error code
        log_event("Error getting user profile: " . $e->getCode() . " - " . $e->getMessage());
    }
}

// User profile form
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!empty($_POST['bio'])) {
        // Validate and sanitize bio input before updating the database
        $_POST['bio'] = trim(filter_var($_POST['bio'], FILTER_SANITIZE_STRING));

        // Sanitize and validate userId to prevent SQL injection attacks
        $userId = (int) filter_input(INPUT_SESSION, 'id', FILTER_VALIDATE_INT);
        if ($userId === false || !isset($_SESSION['id'])) {
            log_event("Invalid user ID: " . $_SESSION['id']);
            exit;
        }

        updateUserProfile($userId, $_POST['bio']);

        // Update the user's session with their new bio
        $_SESSION['bio'] = $_POST['bio'];
    }
}

// Display user profile information
if (isset($_SESSION['id']) && !empty($_SESSION['bio'])) {
    echo "<h2>My Profile:</h2>";
    echo "<p>Bio: " . $_SESSION['bio'] . "</p>";

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        echo "<p>Your bio has been updated!</p>";
    }
}

// Display profile update form
?>
<form action="" method="post">
    <textarea name="bio" cols="40" rows="5"><?= isset($_SESSION['bio']) ? $_SESSION['bio'] : '' ?></textarea>
    <input type="submit" value="Update Bio">
</form>

<a href="#" onclick="logoutUser()">Logout</a>

<?php
// Simplified logout function that only destroys the user's session
function logoutUser() {
    session_destroy();
}
?>
