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
        $this->uploadDirectory = getenv('UPLOAD_DIRECTORY');
    }

    public function addUser(User $user): void
    {
        if (is_int($user->getId()) && ($user->getId() >= 0)) {
            try {
                $connection = new \PDO(
                    'mysql:host=' . getenv('DB_HOST') . ';dbname=' . getenv('DB_NAME'),
                    getenv('DB_USER'),
                    getenv('DB_PASSWORD')
                );

                $connection->setAttribute(\PDO::ATTR_ERRMODE, \PDO::ERRMODE_EXCEPTION);
                $statement = $connection->prepare('INSERT INTO users (id, name) VALUES (:id, :name)');
                $statement->bindParam(':id', $user->getId());
                $statement->bindParam(':name', $user->getName());

                if (!$statement->execute()) {
                    throw new \Exception('Database error: ' . $connection->errorInfo()[2]);
                }
            } catch (\PDOException $e) {
                // Log any database errors securely using the logger
                $logger = new Logger('database_error');
                $logger->error('Error adding user to database: ' . $e->getMessage());
            }
        } else {
            throw new \InvalidArgumentException('Invalid user ID provided');
        }
    }

    public function uploadAvatar(User $user, string $avatarPath): void
    {
        if (is_int($user->getId()) && ($user->getId() >= 0)) {
            try {
                // Validate file extension and size before uploading the avatar
                $allowedExtensions = ['jpg', 'jpeg', 'png'];
                $fileInfo = pathinfo($avatarPath);
                $isValidExtension = in_array(strtolower($fileInfo['extension']), $allowedExtensions);

                if (!$isValidExtension || (filesize($avatarPath) > 1024 * 1024)) {
                    throw new \InvalidArgumentException('Invalid file extension or size');
                }

                // Move the uploaded avatar to the uploads directory
                move_uploaded_file($avatarPath, __DIR__ . '/' . $this->uploadDirectory . '/' . basename($avatarPath));

                // Update the user's avatar in the database using a parameterized query
                $connection = new \PDO(
                    'mysql:host=' . getenv('DB_HOST') . ';dbname=' . getenv('DB_NAME'),
                    getenv('DB_USER'),
                    getenv('DB_PASSWORD')
                );

                $connection->setAttribute(\PDO::ATTR_ERRMODE, \PDO::ERRMODE_EXCEPTION);
                $statement = $connection->prepare('UPDATE users SET avatar = :avatar WHERE id = :id');
                $statement->bindParam(':id', $user->getId());
                $statement->bindParam(':avatar', basename($avatarPath));

                if (!$statement->execute()) {
                    throw new \Exception('Database error: ' . $connection->errorInfo()[2]);
                }
            } catch (\PDOException $e) {
                // Log any database errors securely using the logger
                $logger = new Logger('database_error');
                $logger->error('Error uploading avatar to database: ' . $e->getMessage());
            } catch (\Exception $e) {
                // Log any file upload validation errors securely using the logger
                $logger = new Logger('file_upload_validation');
                $logger->addError('File upload validation error: ' . $e->getMessage());
            }
        } else {
            throw new \InvalidArgumentException('Invalid user ID provided');
        }
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
        if (strlen($this->name) > 255) {
            throw new \InvalidArgumentException('Name exceeds maximum allowed length');
        }

        return $this->name;
    }
}

// Initialize the logger
$logger = new Logger('database_error');

// Create a new UserRepository instance
$userRepository = new UserRepository();

// Add a new user with an avatar image upload
try {
    $userRepository->addUser(new User(1));
    $userRepository->uploadAvatar(new User(1), '/path/to/avatar.jpg');
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
?>
