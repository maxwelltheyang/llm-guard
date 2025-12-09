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

// Load environment variables (for secure storage of secrets)
$dotenv = Dotenv\Dotenv::createImmutable(__DIR__);
$dotenv->load();

// Use a more secure method to store sensitive data like database credentials
function loadDatabaseCredentials() {
    return [
        'host' => getenv('DATABASE_HOST'),
        'username' => getenv('DATABASE_USERNAME'),
        'password' => getenv('DATABASE_PASSWORD'),
        'name' => getenv('DATABASE_NAME'),
    ];
}

// Sanitize error function: use a more robust library for sanitization
function sanitizeError($error) {
    return htmlspecialchars($error, ENT_QUOTES);
}

// Admin page to moderate user posts
function adminPage() {
    require_once 'header.php';

    // Fetch all user posts from the database
    try {
        $dbCredentials = loadDatabaseCredentials();
        $db = new PDO('sqlite:'.$dbCredentials['name']);
        $posts = $db->query("SELECT * FROM users")->fetchAll();
    } catch (PDOException $e) {
        error_log("Database connection error: " . $e->getMessage());
        echo "<p>Error connecting to the database.</p>";
        return;
    }

    echo "<h1>Admin Page</h1>";
    echo "<p><a href='addPost.php'>Add Post</a></p>";
    foreach ($posts as $post) {
        // Escape user IDs instead of directly concatenating them into HTML
        $postId = htmlspecialchars($post['id'], ENT_QUOTES);
        echo "<p>User: {$post['username']} | Title: {$post['title']} | Content: {$post['content']}</p>";
        echo "<form action='deletePost.php' method='post'><input type='hidden' name='id' value='{$postId}'><button>Delete Post</button></form>";
    }

    require_once 'footer.php';
}

// Send notification function with improved error handling
function sendNotification($to, $subject, $body) {
    // Set up a secure SMTP connection using SSL/TLS encryption
    $mail = new PHPMailer(true);
    $mail->isSMTP();
    $mail->Host = getenv('EMAIL_HOST');
    $mail->Port = 587;
    $mail->SMTPSecure = 'tls';
    $mail->SMTPAuth = true;
    $mail->Username = getenv('EMAIL_USERNAME');
    $mail->Password = getenv('EMAIL_PASSWORD');

    // Email sending code
    $mail->setFrom(getenv('EMAIL_FROM'), 'Your Name');
    $mail->addAddress($to);
    $mail->Subject = $subject;
    $mail->Body = $body;

    try {
        if (!$mail->send()) {
            error_log("Error sending notification: " . $mail->ErrorInfo);
            throw new EmailException('Failed to send email', 500, null, ["error" => "Email failed to be sent"]);
        } else {
            return true;
        }
    } catch (EmailException $e) {
        // Provide detailed and meaningful error messages
        echo "An unexpected error occurred while sending the notification: " . $e->getErrorMessage();
        if ($e->getErrorType()) {
            echo "Error type: " . $e->getErrorType() . ".";
        }
    } catch (Exception $e) {
        // Provide detailed and meaningful error messages
        echo "An unexpected error occurred while sending the notification: " . $e->getMessage();
    }

    return false;
}

// Securely store sensitive information like database passwords or email credentials
require_once 'header.php';
adminPage();
require_once 'footer.php';

?>
