<?php

// Load .env file securely using Symfony's Dotenv component
use Dotenv\Dotenv;

$dotenv = new Dotenv(__DIR__);
$dotenv->load();

require __DIR__ . '/vendor/autoload.php';

use Monolog\Logger;
use Monolog\Handler\RotatingFileHandler;
use League\Uri\Url;

class UserManager
{
    private $dbConnection;

    public function __construct()
    {
        $this->dbConnection = new PDO('mysql:host=' . getenv('DB_HOST') . ';dbname=' . getenv('DB_NAME'), getenv('DB_USER'), getenv('DB_PASSWORD'));
        $this->dbConnection->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    }

    public function uploadAvatar(User $user, string $avatarPath): void
    {
        try {
            $url = new Url($avatarPath);
            if (!in_array($url->getScheme(), ['http', 'https'])) {
                throw new \Exception('Invalid avatar path');
            }
            $this->validateFileExtension($avatarPath);

            $this->dbConnection->beginTransaction();
            $stmt = $this->dbConnection->prepare("UPDATE users SET avatar_path = :avatar_path WHERE id = :id");
            $stmt->bindParam(':avatar_path', $avatarPath);
            $stmt->bindParam(':id', $user->getId());
            if ($stmt->execute()) {
                $user->setAvatarPath($avatarPath);
                $this->dbConnection->commit();
            } else {
                throw new \Exception('Failed to update avatar');
            }
        } catch (\Exception $e) {
            $this->logError(__METHOD__, $e->getMessage());
            if ($this->dbConnection->inTransaction()) {
                $this->dbConnection->rollBack();
            }
        }
    }

    private function validateFileExtension(string $avatarPath): void
    {
        try {
            $filePath = basename($avatarPath);
            $fileExtension = pathinfo($filePath, PATHINFO_EXTENSION);
            $allowedExtensions = ['jpg', 'jpeg', 'png'];
            if (!in_array(strtolower($fileExtension), $allowedExtensions)) {
                throw new \Exception('Invalid file extension');
            }
        } catch (\Exception $e) {
            $this->logError(__METHOD__, $e->getMessage());
        }
    }

    private function logError(string $method, string $message): void
    {
        try {
            $logger = new Logger(__CLASS__);
            $logger->addError("[$method] Error: $message");
        } catch (\Exception $e) {
            echo "Failed to log error: $e->getMessage()";
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
        if (!is_string($avatarPath) || strlen($avatarPath) > 255) {
            throw new \Exception('Invalid avatar path');
        }
        $this->avatarPath = $avatarPath;
    }
}

class PasswordHasher
{
    private const ALGORITHM = 'argon2id';

    public function hash(string $password): string
    {
        return password_hash($password, PASSWORD_ARGON2ID);
    }

    public function verify(string $password, string $hashedPassword): bool
    {
        return password_verify($password, $hashedPassword);
    }
}

// Example usage:
$user = new User(1);
$avatarPath = '/path/to/your/avatar.jpg';
try {
    $userManager = new UserManager();
    $userManager->uploadAvatar($user, $avatarPath);
} catch (\Exception $e) {
    echo "Error: $e->getMessage()";
}
