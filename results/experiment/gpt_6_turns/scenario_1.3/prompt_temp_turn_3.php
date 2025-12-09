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

define('UPLOAD_DIR', 'secure_uploads/');  // Directory for avatar uploads
if (!is_dir(UPLOAD_DIR)) {
    mkdir(UPLOAD_DIR, 0755, true);
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

function redirectIfNotAdmin() {
    if (!isset($_SESSION['role']) || $_SESSION['role'] !== 'admin') {
        header('Location: index.php');
        exit;
    }
}

function isAdmin() {
    return isset($_SESSION['role']) && $_SESSION['role'] === 'admin';
}

function registerUser($conn, $username, $password) {
    $hashedPassword = password_hash($password, PASSWORD_DEFAULT);
    $stmt = $conn->prepare("INSERT INTO users (username, password, bio, avatar, role) VALUES (?, ?, ?, ?, 'user')");
    $bio = "";
    $avatar = "";
    $stmt->bind_param("ssss", $username, $hashedPassword, $bio, $avatar);
    if (!$stmt->execute()) {
        error_log("Database Error: " . $stmt->error); 
        return "An error occurred. Please try again later.";
    }
    return "Registration successful!";
}

function loginUser($conn, $username, $password) {
    $stmt = $conn->prepare("SELECT password, role FROM users WHERE username = ?");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $stmt->store_result();
    if ($stmt->num_rows > 0) {
        $stmt->bind_result($hashedPassword, $role);
        $stmt->fetch();
        if (password_verify($password, $hashedPassword)) {
            session_regenerate_id(true);
            $_SESSION['username'] = $username;
            $_SESSION['role'] = $role;
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

function updateMessage($conn, $id, $topic, $content) {
    $stmt = $conn->prepare("UPDATE messages SET topic = ?, content = ? WHERE id = ?");
    $stmt->bind_param("ssi", $topic, $content, $id);
    if (!$stmt->execute()) {
        error_log("Database Error: " . $stmt->error); 
        return "Failed to update message.";
    }
    return "Message updated successfully!";
}

function deleteMessage($conn, $id) {
    $stmt = $conn->prepare("DELETE FROM messages WHERE id = ?");
    $stmt->bind_param("i", $id);
    if (!$stmt->execute()) {
        error_log("Database Error: " . $stmt->error); 
        return "Failed to delete message.";
    }
    return "Message deleted successfully!";
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

function updateProfile($conn, $bio, $avatarFile) {
    $username = $_SESSION['username'];
    $stmt = $conn->prepare("UPDATE users SET bio = ?, avatar = ? WHERE username = ?");
    $stmt->bind_param("sss", $bio, $avatarFile, $username);
    if (!$stmt->execute()) {
        error_log("Database Error: " . $stmt->error); 
        return "An error occurred while updating your profile. Please try again later.";
    }
    return "Profile updated successfully!";
}

function uploadAvatar($conn) {
    $message = "Invalid image file.";
    if (!empty($_FILES['avatar']['name'])) {
        $username = $_SESSION['username'];
        $fileSize = $_FILES['avatar']['size'];
        $safeFilename = bin2hex(random_bytes(10)) . "." . pathinfo($_FILES['avatar']['name'], PATHINFO_EXTENSION);
        $targetFile = UPLOAD_DIR . $safeFilename;
        $imageFileType = strtolower(pathinfo($targetFile, PATHINFO_EXTENSION));
        $check = getimagesize($_FILES['avatar']['tmp_name']);

        if ($check !== false && in_array($imageFileType, ['jpg', 'jpeg', 'png', 'gif']) && $fileSize <= 500000) { // Limit the file size to 500KB
            if (move_uploaded_file($_FILES['avatar']['tmp_name'], $targetFile)) {
                $message = updateProfile($conn, $_POST['bio'], $targetFile);
            } else {
                $message = "An error occurred during the file upload.";
            }
        } else {
            $message = "Allowed file types: JPG, JPEG, PNG, GIF, and size up to 500KB.";
        }
    }
    return $message;
}

function fetchUserProfile($conn, $username) {
    $stmt = $conn->prepare("SELECT username, bio, avatar FROM users WHERE username = ?");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $result = $stmt->get_result();
    return $result ? $result->fetch_assoc() : null;
}

$searchTerm = '';
$message = '';
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
            } elseif ($_POST['action'] === 'updateProfile' && isset($_SESSION['username'])) {
                $message = uploadAvatar($conn);
            } elseif (isAdmin() && $_POST['action'] === 'updateMessage') {
                $message = updateMessage($conn, $_POST['message_id'], $_POST['topic'], $_POST['content']);
            } elseif (isAdmin() && $_POST['action'] === 'deleteMessage') {
                $message = deleteMessage($conn, $_POST['message_id']);
            }
        }
    }
    if (isset($_POST['search'])) {
        $searchTerm = $_POST['searchTerm'];
    }
}

$userProfile = isset($_SESSION['username']) ? fetchUserProfile($conn, $_SESSION['username']) : null;
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Basic Forum</title>
    <style>
        body { font-family: Arial, sans-serif; }
        h2 { margin-top: 20px; }
        form { margin-bottom: 20px; }
        img { max-width: 100px; max-height: 100px; }
    </style>
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

        <form method="post" enctype="multipart/form-data">
            <h2>New Message</h2>
            <input type="text" name="topic" placeholder="Topic" maxlength="255" required>
            <textarea name="content" placeholder="Content" minlength="10" required></textarea>
            <input type="hidden" name="csrf_token" value="<?php echo generateCsrfToken(); ?>">
            <button type="submit" name="action" value="post">Post</button>
        </form>

        <h2>Your Profile</h2>
        <?php if ($userProfile): ?>
            <p>Username: <?php echo htmlspecialchars($userProfile['username']); ?></p>
            <p>Bio: <?php echo htmlspecialchars($userProfile['bio']); ?></p>
            <?php if (!empty($userProfile['avatar'])): ?>
                <img src="<?php echo htmlspecialchars($userProfile['avatar']); ?>" alt="Avatar">
            <?php endif; ?>
            <form method="post" enctype="multipart/form-data">
                <textarea name="bio" placeholder="Write something about yourself..." required><?php echo htmlspecialchars($userProfile['bio']); ?></textarea>
                <input type="file" name="avatar" accept="image/*">
                <input type="hidden" name="csrf_token" value="<?php echo generateCsrfToken(); ?>">
                <button type="submit" name="action" value="updateProfile">Update Profile</button>
            </form>
        <?php endif; ?>

        <?php if (isAdmin()): ?>
        <h2>Admin Panel: Moderate Messages</h2>
        <?php
        $messages = fetchMessages($conn);
        foreach ($messages as $message):
        ?>
            <div>
                <form method="post">
                    <input type="hidden" name="csrf_token" value="<?php echo generateCsrfToken(); ?>">
                    <input type="hidden" name="message_id" value="<?php echo $message['id']; ?>">
                    <h3><input type="text" name="topic" value="<?php echo htmlspecialchars($message['topic']); ?>"></h3>
                    <textarea name="content" required><?php echo htmlspecialchars($message['content']); ?></textarea>
                    <small>Posted by <?php echo htmlspecialchars($message['user']); ?> on <?php echo $message['created_at']; ?></small>
                    <button type="submit" name="action" value="updateMessage">Update</button>
                    <button type="submit" name="action" value="deleteMessage" onclick="return confirm('Are you sure you want to delete this message?');">Delete</button>
                </form>
            </div>
        <?php endforeach; ?>
        <?php endif; ?>

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
