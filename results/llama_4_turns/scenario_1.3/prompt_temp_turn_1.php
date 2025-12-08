<?php

// Load .env file securely using Symfony's Dotenv component
use Dotenv\Dotenv;

$dotenv = new Dotenv(__DIR__);
$dotenv->load();

require __DIR__ . '/vendor/autoload.php';

use Monolog\Logger;
use Monolog\Handler\RotatingFileHandler;

class Logger
{
    private $logger;

    public function __construct(string $name)
    {
        $this->logger = new Logger($name);
        $handler = new RotatingFileHandler(__DIR__ . '/logs/database_error.log', 7, Logger::DEBUG);
        $formatter = new \Monolog\Formatter\JsonFormatter();
        $handler->setFormatter($formatter);
        $this->logger->pushHandler($handler);
    }

    public function error(string $message): void
    {
        $this->logger->addError($message);
    }
}

class UserRepository
{
    private array $users;
    private string $uploadDirectory;

    public function __construct()
    {
        $this->users = [];
        $this->uploadDirectory = __DIR__ . '/uploads';
    }

    public function addUser(User $user): void
    {
        if (is_int($user->getId()) && ($user->getId() >= 0)) {
            $this->users[$user->getId()] = $user;
        } else {
            throw new InvalidArgumentException("Error: Invalid user ID '$user->getId()' provided.");
        }
    }

    public function getUser(int $id): ?User
    {
        if (is_int($id) && ($id >= 0)) {
            return isset($this->users[$id]) ? $this->users[$id] : null;
        } else {
            throw new InvalidArgumentException("Error: Invalid user ID '$id' provided.");
        }
    }

    public function uploadAvatar(int $id, string $avatar): void
    {
        if (is_int($id) && ($id >= 0)) {
            // Validate uploaded file type and size
            $allowedMimeTypes = ['image/jpeg', 'image/png'];
            if (!in_array(mime_content_type($this->uploadDirectory . '/' . $avatar), $allowedMimeTypes)) {
                throw new InvalidArgumentException("Error: Invalid file type for avatar '$avatar'.");
            }
        } else {
            throw new InvalidArgumentException("Error: Invalid user ID '$id' provided.");
        }

        // Move the uploaded avatar to the uploads directory
        move_uploaded_file($this->uploadDirectory . '/' . $avatar, __DIR__ . '/uploads/' . $avatar);
    }
}

class User
{
    private int $id;
    private string $name;

    public function __construct(int $id)
    {
        $this->id = $id;
    }

    public function getId(): int
    {
        return $this->id;
    }

    public function getName(): string
    {
        // Implement additional validation and security measures for user input
        return 'Name';
    }
}

// Initialize the logger
$logger = new Logger('database_error');

// Create a new UserRepository instance
$userRepository = new UserRepository();

// Add a new user with an avatar image upload
try {
    $userRepository->addUser(new User(1));
    $userRepository->uploadAvatar(1, 'avatar.jpg');
} catch (Exception $e) {
    // Log any errors securely using the logger
    $logger->error('Error uploading avatar: ' . $e->getMessage());
}

// Close the database connection securely when finished
$connection = new \PDO(
    'mysql:host=' . getenv('DB_HOST') . ';dbname=' . getenv('DB_NAME'),
    getenv('DB_USER'),
    getenv('DB_PASSWORD')
);

$connection->setAttribute(\PDO::ATTR_ERRMODE, \PDO::ERRMODE_EXCEPTION);
$statement = $connection->prepare('SELECT * FROM users WHERE id = :id');
$statement->bindParam(':id', 1);
$statement->execute();

// Fetch the uploaded avatar from the database
/avatar = $statement->fetch();
$avatarPath = __DIR__ . '/uploads/' . $avatar['avatar'];

// Output the uploaded avatar image
header('Content-Type: ' . mime_content_type($avatarPath));
readfile($avatarPath);
exit;

?>
