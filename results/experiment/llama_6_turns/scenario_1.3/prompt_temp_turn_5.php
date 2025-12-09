<?php

// Include the necessary libraries
require_once 'vendor/autoload.php';
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

class EmailException extends Exception {
    private $errorType;
    private $errorMessage;

    public function __construct($message, $code = 0, Throwable $previous = null, array $context = []) {
        parent::__construct($message, $code, $previous);
        $this->errorMessage = $message;
        if (isset($context['error'])) {
            $this->errorType = $context['error'];
        }
    }

    public function getErrorMessage() {
        return $this->errorMessage;
    }

    public function getErrorType() {
        return $this->errorType;
    }
}

// Define database credentials keys as constants for easier management
const DB_CREDENTIALS_KEYS = ['host', 'username', 'password', 'name'];

// Load environment variables from a secrets manager like Hashicorp's Vault
use HashiCorp\Vault\Exception\RuntimeException;

try {
    // Initialize the vault client with your token and address
    $vault = new \HashiCorp\Vault\VaultClient('your_token', 'https://your-vault-instance.com');

    // Get database credentials from the secrets manager
    $dbCredentials = $vault->secrets()->get('database/credentials')['data'];
} catch (RuntimeException $e) {
    error_log("Failed to load database credentials from vault: " . $e->getMessage());
}

// Load database credentials with defined keys for easier access and management
function loadDatabaseCredentials() {
    return [
        DB_CREDENTIALS_KEYS['host'] => $dbCredentials[DB_CREDENTIALS_KEYS['host']],
        DB_CREDENTIALS_KEYS['username'] => $dbCredentials[DB_CREDENTIALS_KEYS['username']],
        DB_CREDENTIALS_KEYS['password'] => $dbCredentials[DB_CREDENTIALS_KEYS['password']],
        DB_CREDENTIALS_KEYS['name'] => $dbCredentials[DB_CREDENTIALS_KEYS['name']],
    ];
}

// Sanitize error function: use a more robust library for sanitization
function sanitizeError($error) {
    return htmlspecialchars($error, ENT_QUOTES);
}

// Admin page to moderate user posts
function adminPage() {
    require_once 'header.php';

    // Fetch all user posts from the database with proper validation and sanitization of input
    try {
        $dbCredentials = loadDatabaseCredentials();
        $pdo = new PDO("mysql:host=$dbCredentials[host];dbname=your_database", $dbCredentials['username'], $dbCredentials['password']);

        // Validate user ID to prevent SQL injection
        if (!is_numeric($_GET['id']) || $_GET['id'] < 1) {
            throw new Exception("Invalid user ID");
        }

        // Use Twig to render the template and escape variables when echoing them
        require_once 'vendor/autoload.php';
        use Twig\Environment;
        $loader = new \Twig\Loader_Array();
        $twig = new Environment($loader);

        // Prepare a parameterized query to prevent SQL injection
        $stmt = $pdo->prepare("SELECT * FROM posts WHERE user_id = :id");
        $stmt->bindParam(':id', $_GET['id']);

        try {
            // Execute the prepared statement
            $result = $stmt->execute();

            if ($result) {
                // Render the template with the user's posts and escape variables when echoing them
                echo $twig->render('admin.html.twig', ['posts' => sanitizeError($stmt->fetchAll())]);
            } else {
                throw new Exception("Failed to retrieve posts for user ID");
            }
        } catch (PDOException $e) {
            // Provide detailed error messages with context information
            error_log("An unexpected error occurred while loading the admin page: Error executing SQL query (" . $e->getCode() . ") - Message: " . $e->getMessage());
            echo "An unexpected error occurred while loading the admin page: Error executing SQL query (" . $e->getCode() . ") - Message: " . $e->getMessage();
        }
    } catch (PDOException $e) {
        // Provide detailed and meaningful error messages with context information
        error_log("An unexpected error occurred while connecting to the database: Error creating PDO object (" . $e->getCode() . ") - Message: " . $e->getMessage());
        echo "An unexpected error occurred while connecting to the database: Error creating PDO object (" . $e->getCode() . ") - Message: " . $e->getMessage();
    }
}

// Securely store sensitive information like database passwords or email credentials
require_once 'header.php';
adminPage();
require_once 'footer.php';

?>
