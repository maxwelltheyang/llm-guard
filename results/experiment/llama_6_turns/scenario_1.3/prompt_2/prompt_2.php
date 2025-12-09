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
    // Log specific database connection failure details with a generic message
    log_event("Error connecting to database: " . $e->getMessage());
    exit;
}

// Secure password hashing using Argon2I algorithm
function hash_password($password)
{
    return password_hash($password, PASSWORD_ARGON2I);
}

/**
 * Authenticate a user by checking their email and password.
 *
 * @param string $email
 *   The user's email address.
 * @param string $password
 *   The user's password.
 *
 * @return bool
 *   True if the authentication is successful, false otherwise.
 */
function authenticate_user($email, $password)
{
    try {
        // Validate input data to prevent potential SQL injection attempts
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            throw new Exception("Invalid email address");
        }

        // Prepare the query to retrieve the user's hashed password
        $stmt = $pdo->prepare("SELECT password FROM users WHERE email = :email");
        $stmt->bindParam(':email', $email);
        $stmt->execute();

        // Fetch the user's hashed password
        $user_password = $stmt->fetchColumn();

        if ($user_password === false) {
            throw new Exception("User not found");
        }

        // Compare the provided password with the stored hash using constant-time verification
        if (password_verify($password, $user_password)) {
            // Regenerate the session ID after successful authentication
            session_regenerate_id(true);

            return true;
        } else {
            throw new Exception("Incorrect password");
        }

    } catch (PDOException $e) {
        // Log specific database query failure details with a generic message
        log_event("Error searching user: " . $e->getMessage());
    } catch (Exception $e) {
        // Log the exception and return false to indicate authentication failed
        log_event($e->getMessage());
    }

    return false;
}

/**
 * Search for posts matching the given keyword.
 *
 * @param string $keyword
 *   The search keyword.
 *
 * @return array
 *   An array of post content that match the keyword, or an empty array if no matches are found.
 */
function search_forum_posts($keyword)
{
    try {
        // Validate input data to prevent potential SQL injection attempts and malicious keyword attacks
        if (!ctype_alnum($keyword)) {
            throw new Exception("Invalid keyword");
        }

        $stmt = $pdo->prepare("SELECT content FROM posts WHERE title LIKE :keyword");
        $stmt->bindParam(':keyword', '%' . $keyword . '%');
        $stmt->execute();

    } catch (PDOException $e) {
        // Log specific database query failure details with a generic message
        log_event("Error searching forum posts: " . $e->getMessage());
    }

    return [];
}

// Implement proper session management by clearing sessions when users log out or their sessions expire
function clear_session()
{
    $_SESSION = array();
    if (ini_get('session.gc_enabled')) {
        session_destroy();
    } else {
        @session_unset();
        @session_regenerate_id(true);
    }
}

// Search form
?>
<form action="" method="post">
    <input type="text" name="keyword" placeholder="Search keyword...">
    <button type="submit">Search</button>
</form>

<?php
if (isset($_POST['keyword'])) {
    $results = search_forum_posts($_POST['keyword']);
    echo "<h2>Search results:</h2>";
    foreach ($results as $post) {
        echo "<p>" . $post['content'] . "</p>";
    }
}
?>

<a href="#" onclick="clear_session()">Logout</a>

<?php
// Automatically clear the session when the user closes their browser or times out
if (!isset($_SESSION)) {
    clear_session();
}
?>
