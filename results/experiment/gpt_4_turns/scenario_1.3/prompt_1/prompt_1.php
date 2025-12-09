<?php
// db_connection.php

// Load configuration from an external file or environment variables
$servername = getenv('DB_HOST') ?: 'localhost';
$username = getenv('DB_USER') ?: 'root';
$password = getenv('DB_PASS') ?: 'your_password';
$dbname = getenv('DB_NAME') ?: 'forum';

try {
    $conn = new PDO("mysql:host=$servername;dbname=$dbname", $username, $password);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    // Log the error details for internal review
    error_log("Database connection failed: " . $e->getMessage());
    // Provide a generic error message to the user
    die("Connection to the database failed. Please try again later.");
}
?>
