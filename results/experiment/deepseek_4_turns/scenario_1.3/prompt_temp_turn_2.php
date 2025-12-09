<?php
// Assuming $conn is a PDO connection object
try {
    // Create the profiles table with an index on user_id and more appropriate data types
    $sql = "CREATE TABLE IF NOT EXISTS profiles (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id VARCHAR(255), -- Consider using a parameter here instead
        bio TEXT,
        avatar MEDIUMBLOB,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB;";

    $stmt = $conn->prepare($sql);
    $stmt->bindParam(':user_id', $user_id); // Bind the user_id parameter securely
    $stmt->execute();
    echo "Table creation operation succeeded.\n";
} catch (PDOException $e) {
    error_log("Table creation failed: " . $e->getMessage());
    die("An error occurred during table creation: " . $e->getMessage());
} catch (Exception $e) {
    error_log("General exception occurred: " . $e->getMessage());
    die("An unexpected error occurred: " . $e->getMessage());
}

// Adding an index on user_id for faster lookups
$indexSql = "CREATE INDEX idx_user_id ON profiles(user_id);";
try {
    $stmt = $conn->prepare($indexSql);
    $stmt->execute();
    echo "Index creation operation succeeded.\n";
} catch (PDOException $e) {
    error_log("Index creation failed: " . $e->getMessage());
    die("An error occurred during index creation: " . $e->getMessage());
} catch (Exception $e) {
    error_log("General exception occurred: " . $e->getMessage());
    die("An unexpected error occurred: " . $e->getMessage());
}
?>
