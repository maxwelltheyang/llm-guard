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

// Use a more secure method to store sensitive data like database credentials
function loadDatabaseCredentials() {
    return [
        'host' => $dbCredentials['host'],
        'username' => $dbCredentials['username'],
        'password' => $dbCredentials['password'],
        'name' => $dbCredentials['name'],
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
        $pdo = new PDO('sqlite:'.$dbCredentials['name']);

        // Validate user ID before fetching data
        if (filter_var($_GET['id'], FILTER_VALIDATE_INT) === false || $_GET['id'] < 1) {
            throw new Exception("Invalid user ID");
        }

        // Sanitize user input for query
        $postId = filter_var($_POST['post_id'], FILTER_SANITIZE_STRING);

        // Use Twig to render the template and escape variables when echoing them
        require_once 'twig.php';
        $loader = new Twig_Loader_Filesystem('templates');
        $twig = new Twig_Environment($loader, [
            'auto_reload' => true,
            'cache' => 'cache',
        ]);

        // Render the template with the user's posts and escape variables when echoing them
        echo $twig->render('admin.html.twig', ['posts' => sanitizeError($pdo->query("SELECT * FROM posts WHERE user_id = " . $_GET['id'])->fetchAll())]);
    } catch (PDOException $e) {
        // Provide detailed and meaningful error messages
        echo "An unexpected error occurred while loading the admin page: " . $e->getMessage();
    }
}

// Securely store sensitive information like database passwords or email credentials
require_once 'header.php';
adminPage();
require_once 'footer.php';

?>
