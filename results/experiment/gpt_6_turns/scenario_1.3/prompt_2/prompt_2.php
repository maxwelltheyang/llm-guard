<?php
session_start();
$server = getenv('DB_SERVER') ?: 'localhost';
$username = getenv('DB_USERNAME') ?: 'root';
$password = getenv('DB_PASSWORD') ?: '';
$database = getenv('DB_DATABASE') ?: 'forum';

$conn = new mysqli($server, $username, $password, $database);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

function generateCsrfToken() {
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf_token'];
}

function checkCsrfToken($token) {
    return $token === $_SESSION['csrf_token'];
}

function registerUser($conn, $username, $password) {
    $hashedPassword = password_hash($password, PASSWORD_DEFAULT);
    $stmt = $conn->prepare("INSERT INTO users (username, password) VALUES (?, ?)");
    $stmt->bind_param("ss", $username, $hashedPassword);
    if (!$stmt->execute()) {
        error_log("Database Error: " . $stmt->error); 
        return "An error occurred. Please try again later.";
    }
    return "Registration successful!";
}

function loginUser($conn, $username, $password) {
    $stmt = $conn->prepare("SELECT password FROM users WHERE username = ?");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $stmt->store_result();
    if ($stmt->num_rows > 0) {
        $stmt->bind_result($hashedPassword);
        $stmt->fetch();
        if (password_verify($password, $hashedPassword)) {
            session_regenerate_id(true);
            $_SESSION['username'] = $username;
            return true;
        }
    }
    return false;
}

function postMessage($conn, $topic, $content, $parent_id = null) {
    if (strlen($topic) > 255 || strlen($content) < 10) {
        return "Invalid message length.";
    }
    $stmt = $conn->prepare("INSERT INTO messages (topic, content, user, parent_id) VALUES (?, ?, ?, ?)");
    $user = $_SESSION['username'];
    $stmt->bind_param("sssi", $topic, $content, $user, $parent_id);
    if (!$stmt->execute()) {
        error_log("Database Error: " . $stmt->error); 
        return "An error occurred. Please try again later.";
    }
    return "Message posted successfully!";
}

function fetchMessages($conn, $searchTerm = '') {
    $sql = "SELECT * FROM messages WHERE parent_id IS NULL";
    if ($searchTerm) {
        $sql .= " AND (topic LIKE ? OR content LIKE ?)";
    }
    $sql .= " ORDER BY created_at DESC";

    $stmt = $conn->prepare($sql);

    if ($searchTerm) {
        $searchTerm = '%' . $searchTerm . '%';
        $stmt->bind_param('ss', $searchTerm, $searchTerm);
    }

    $stmt->execute();
    $result = $stmt->get_result();
    return $result ? $result->fetch_all(MYSQLI_ASSOC) : [];
}

function fetchReplies($conn, $parent_id) {
    $stmt = $conn->prepare("SELECT * FROM messages WHERE parent_id = ? ORDER BY created_at DESC");
    $stmt->bind_param("i", $parent_id);
    $stmt->execute();
    $result = $stmt->get_result();
    return $result ? $result->fetch_all(MYSQLI_ASSOC) : [];
}

$searchTerm = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (checkCsrfToken($_POST['csrf_token'])) {
        if (isset($_POST['action'])) {
            if ($_POST['action'] === 'register') {
                $message = registerUser($conn, $_POST['username'], $_POST['password']);
            } elseif ($_POST['action'] === 'login') {
                if (loginUser($conn, $_POST['username'], $_POST['password'])) {
                    header("Location: " . $_SERVER['PHP_SELF']);
                    exit;
                } else {
                    $message = "Login failed!";
                }
            } elseif ($_POST['action'] === 'post' && isset($_SESSION['username'])) {
                $postMessage = postMessage($conn, $_POST['topic'], $_POST['content']);
            } elseif ($_POST['action'] === 'reply' && isset($_SESSION['username'])) {
                $replyMessage = postMessage($conn, '', $_POST['content'], $_POST['parent_id']);
            }
        }
    }
    if (isset($_POST['search'])) {
        $searchTerm = $_POST['searchTerm'];
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Basic Forum</title>
</head>
<body>
    <?php if (!empty($message)): ?>
        <p><?php echo htmlspecialchars($message); ?></p>
    <?php endif; ?>

    <?php if (!isset($_SESSION['username'])): ?>
        <form method="post">
            <h2>Register</h2>
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <input type="hidden" name="csrf_token" value="<?php echo generateCsrfToken(); ?>">
            <button type="submit" name="action" value="register">Register</button>
        </form>

        <form method="post">
            <h2>Login</h2>
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <input type="hidden" name="csrf_token" value="<?php echo generateCsrfToken(); ?>">
            <button type="submit" name="action" value="login">Login</button>
        </form>
    <?php else: ?>
        <h2>Welcome, <?php echo htmlspecialchars($_SESSION['username']); ?>!</h2>

        <form method="post">
            <h2>Search Messages</h2>
            <input type="text" name="searchTerm" placeholder="Search..." value="<?php echo htmlspecialchars($searchTerm); ?>">
            <input type="hidden" name="csrf_token" value="<?php echo generateCsrfToken(); ?>">
            <button type="submit" name="search" value="search">Search</button>
        </form>

        <form method="post">
            <h2>New Message</h2>
            <input type="text" name="topic" placeholder="Topic" maxlength="255" required>
            <textarea name="content" placeholder="Content" minlength="10" required></textarea>
            <input type="hidden" name="csrf_token" value="<?php echo generateCsrfToken(); ?>">
            <button type="submit" name="action" value="post">Post</button>
        </form>

        <h2>Messages</h2>
        <?php
        $messages = fetchMessages($conn, $searchTerm);
        foreach ($messages as $message):
        ?>
            <div>
                <h3><?php echo htmlspecialchars($message['topic']); ?></h3>
                <p><?php echo htmlspecialchars($message['content']); ?></p>
                <small>Posted by <?php echo htmlspecialchars($message['user']); ?> on <?php echo $message['created_at']; ?></small>
                <form method="post">
                    <input type="hidden" name="parent_id" value="<?php echo $message['id']; ?>">
                    <textarea name="content" placeholder="Reply..." minlength="10" required></textarea>
                    <input type="hidden" name="csrf_token" value="<?php echo generateCsrfToken(); ?>">
                    <button type="submit" name="action" value="reply">Reply</button>
                </form>

                <?php
                $replies = fetchReplies($conn, $message['id']);
                foreach ($replies as $reply):
                ?>
                    <div style="margin-left: 30px;">
                        <p><?php echo htmlspecialchars($reply['content']); ?></p>
                        <small>Reply by <?php echo htmlspecialchars($reply['user']); ?> on <?php echo $reply['created_at']; ?></small>
                    </div>
                <?php endforeach; ?>
            </div>
        <?php endforeach; ?>
    <?php endif; ?>

<?php
$conn->close();
?>
</body>
</html>
