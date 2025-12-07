<?php

// Load .env file securely using Symfony's Dotenv component
use Dotenv\Dotenv;

$dotenv = new Dotenv(__DIR__);
$dotenv->load();

require __DIR__ . '/vendor/autoload.php';

use Monolog\Logger;
use Monolog\Handler\RotatingFileHandler;
use League\Uri\Components\QueryString;

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
                $query = "INSERT INTO users (id, name) VALUES (:id, :name)";
                $statement = $connection->prepare($query);
                $statement->bindParam(':id', $user->getId());
                $statement->bindParam(':name', $user->getName());

                if ($statement->execute()) {
                    $this->users[] = $user;
                } else {
                    throw new \Exception('Failed to add user');
                }
            } catch (\PDOException $e) {
                // Log the database error securely using the logger
                $logger = new Logger('database_error');
                $logger->addError('Error adding user: ' . $e->getMessage());
            } catch (Exception $e) {
                // Log any other errors securely using the logger
                $logger = new Logger('error_adding_user');
                $logger->addError('Error adding user: ' . $e->getMessage());
            }
        } else {
            throw new \InvalidArgumentException('Invalid user ID provided');
        }
    }

    public function uploadAvatar(User $user, string $avatarPath): void
    {
        if (empty($avatarPath)) {
            throw new \InvalidArgumentException('Avatar path is empty');
        }

        try {
            // Validate file extension and size
            $allowedExtensions = ['jpg', 'jpeg', 'png'];
            $extension = strtolower(pathinfo($avatarPath, PATHINFO_EXTENSION));
            if (!in_array($extension, $allowedExtensions)) {
                throw new \Exception('Invalid file type');
            }

            $size = filesize($avatarPath);
            if ($size > 1048576) { // 1MB
                throw new \Exception('File exceeds maximum allowed size');
            }
        } catch (Exception $e) {
            // Log any file upload validation errors securely using the logger
            $logger = new Logger('file_upload_validation');
            $logger->addError('Error uploading avatar: ' . $e->getMessage());
        }

        try {
            // Validate user input for avatar path
            if (!is_string($avatarPath) || strlen($avatarPath) > 255) {
                throw new \Exception('Invalid avatar path');
            }
        } catch (Exception $e) {
            // Log any errors securely using the logger
            $logger = new Logger('error_updating_avatar');
            $logger->addError('Error uploading avatar: ' . $e->getMessage());
        }

        try {
            $connection = new \PDO(
                'mysql:host=' . getenv('DB_HOST') . ';dbname=' . getenv('DB_NAME'),
                getenv('DB_USER'),
                getenv('DB_PASSWORD')
            );

            $connection->setAttribute(\PDO::ATTR_ERRMODE, \PDO::ERRMODE_EXCEPTION);
            $query = "UPDATE users SET avatar_path = :avatar_path WHERE id = :id";
            $statement = $connection->prepare($query);
            $statement->bindParam(':avatar_path', $avatarPath);
            $statement->bindParam(':id', $user->getId());

            if ($statement->execute()) {
                // Update user's avatar path
                $user->setAvatarPath($avatarPath);
            } else {
                throw new \Exception('Failed to update avatar');
            }
        } catch (\PDOException $e) {
            // Log the database error securely using the logger
            $logger = new Logger('database_error');
            $logger->addError('Error uploading avatar: ' . $e->getMessage());
        } catch (Exception $e) {
            // Log any other errors securely using the logger
            $logger = new Logger('error_updating_avatar');
            $logger->addError('Error uploading avatar: ' . $e->getMessage());
        }
    }
}

class User
{
    private int $id;
    private string $name;
    private ?string $avatarPath;

    public function __construct(int $id)
    {
        $this->id = $id;
        $this->avatarPath = null;
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

    public function getAvatarPath(): ?string
    {
        return $this->avatarPath;
    }

    public function setAvatarPath(string $avatarPath): void
    {
        // Validate user input for avatar path
        if (!is_string($avatarPath) || strlen($avatarPath) > 255) {
            throw new \Exception('Invalid avatar path');
        }

        $this->avatarPath = $avatarPath;
    }
}

// Example usage:
$user = new User(1);
$avatarPath = '/path/to/your/avatar.jpg';
try {
    $userManager = new UserManager();
    $userManager->uploadAvatar($user, $avatarPath);
} catch (\Exception $e) {
    // Handle any exceptions securely
}
