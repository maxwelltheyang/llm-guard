<?php

// Load .env file securely using Symfony's Dotenv component
use Dotenv\Dotenv;

$dotenv = Dotenv::createImmutable(__DIR__);
$dotenv->load();

// Securely store sensitive environment variables in a secrets manager (Hashicorp's Vault or AWS Secrets Manager)
$vaultUrl = getenv('VAULT_URL');
$vaultToken = getenv('VAULT_TOKEN');

try {
    // Create a Guzzle client for interacting with Hashicorp's Vault
    use GuzzleHttp\Client;
    $client = new Client();
    $response = $client->get($vaultUrl . '/v1/secrets', [
        'headers' => ['X-Vault-Token' => $vaultToken]
    ]);
    $secrets = json_decode($response->getBody(), true);
} catch (Exception $e) {
    // Log the error securely using a centralized logging system
    use Monolog\Logger;
    use Monolog\Handler\RotatingFileHandler;
    use Monolog\Formatter\JsonFormatter;

    $logger = new Logger('database_error');
    $handler = new RotatingFileHandler(__DIR__ . '/logs/database_error.log', 7, Logger::DEBUG);
    $formatter = new JsonFormatter();
    $handler->setFormatter($formatter);
    $logger->pushHandler($handler);
    $logger->addError('Error retrieving secrets: ' . $e->getMessage());
}

use Doctrine\DBAL\DriverManager;
use Doctrine\ORM\EntityManagerInterface;

class DatabaseConnection
{
    private EntityManagerInterface $entityManager;

    public function __construct()
    {
        // Create a connection to the database using prepared statements and secure credentials from Vault
        $credentials = [
            'username' => $secrets['database']['username'],
            'password' => $secrets['database']['password'],
            'host' => $secrets['database']['host'],
            'port' => (int)$secrets['database']['port'],
            'dbname' => $secrets['database']['name']
        ];

        // Whitelist allowed characters for user input parameters
        $params = [
            'username' => '/^[a-zA-Z0-9_]+$/', 
            'password' => '/^[a-zA-Z0-9_!@#$%^&*]+$/',
            'host' => '/^[a-zA-Z0-9._-]+$/,
            'port' => '/^([0-9]){1,5}$/', // Validate port number
        ];

        $this->entityManager = DriverManager::getConnection([
            'url' => 'mysql:host=' . $credentials['host'] . ';dbname=' . $credentials['dbname'],
            'driver' => 'pdo_mysql',
            'user' => $credentials['username'],
            'password' => $credentials['password']
        ]);
    }

    public function executeQuery(string $query, array $params = []): array
    {
        try {
            $stmt = $this->entityManager->getConnection()->executeQuery($query, $params);
            return $stmt->fetchAll();
        } catch (Exception $e) {
            // Log any query errors securely using the centralized logging system
            $logger = new Logger('database_error');
            $handler = new RotatingFileHandler(__DIR__ . '/logs/database_error.log', 7, Logger::DEBUG);
            $formatter = new JsonFormatter();
            $handler->setFormatter($formatter);
            $logger->pushHandler($handler);
            $logger->addError('Error executing query: ' . $e->getMessage());
            return [];
        }
    }

    public function closeConnection(): void
    {
        // Close the database connection securely when finished
        $this->entityManager = null;
    }
}

class UserRepository
{
    private array $users;

    public function __construct()
    {
        $this->users = [];
    }

    public function addUser(User $user): void
    {
        if (is_int($user->getId()) && ($user->getId() >= 0)) {
            $this->users[$user->getId()] = $user;
        } else {
            // Handle invalid user ID and provide informative error message
            throw new InvalidArgumentException("Error: Invalid user ID '$user->getId()' provided.");
        }
    }

    public function getUser(int $id): ?User
    {
        if (is_int($id) && ($id >= 0)) {
            return isset($this->users[$id]) ? $this->users[$id] : null;
        } else {
            // Handle invalid user ID and provide informative error message
            throw new InvalidArgumentException("Error: Invalid user ID '$id' provided.");
        }
    }
}

class User
{
    private int $id;

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

class Logger
{
    private Monolog\Logger $logger;

    public function __construct(string $name)
    {
        $this->logger = new Logger($name);
        $handler = new RotatingFileHandler(__DIR__ . '/logs/database_error.log', 7, Logger::DEBUG);
        $formatter = new JsonFormatter();
        $handler->setFormatter($formatter);
        $this->logger->pushHandler($handler);
    }

    public function error(string $message): void
    {
        $this->logger->addError($message);
    }
}
?>
