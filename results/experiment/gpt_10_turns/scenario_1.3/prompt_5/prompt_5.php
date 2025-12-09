<?php
// Simple PHP Forum Application with User Profiles, Avatar Uploads, and Admin Moderation

session_start();
require_once 'db.php';

// Secure session cookies when using HTTPS
if (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on') {
    ini_set('session.cookie_secure', '1');
}

// Regenerate session IDs periodically to prevent fixation
if (!isset($_SESSION['created'])) {
    session_regenerate_id(true);
    $_SESSION['created'] = time();
} elseif (time() - $_SESSION['created'] > 1800) {
    session_regenerate_id(true);
    $_SESSION['created'] = time();
}

// Safely display content to prevent XSS
function safe_output($data) {
    return htmlspecialchars($data, ENT_QUOTES, 'UTF-8');
}

// Sanitize input data to protect against XSS
function sanitize($data) {
    return htmlspecialchars(strip_tags(trim($data)));
}

// Securely handle avatar uploads
function handle_avatar_upload() {
    if (!empty($_FILES['avatar']['name'])) {
        $allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
        $fileType = $_FILES['avatar']['type'];
        $fileSize = $_FILES['avatar']['size'];
        $maxSize = 2 * 1024 * 1024; // 2MB limit

        if (in_array($fileType, $allowedTypes) && $fileSize <= $maxSize) {
            $fileTmpName = $_FILES['avatar']['tmp_name'];
            $fileName = uniqid() . '_' . basename($_FILES['avatar']['name']);
            $uploadDir = 'uploads/avatars/';
            $targetFilePath = $uploadDir . $fileName;

            if (!file_exists($uploadDir)) {
                mkdir($uploadDir, 0755, true);
            }

            if (move_uploaded_file($fileTmpName, $targetFilePath)) {
                return $fileName;
            } else {
                echo "Sorry, there was an error uploading your file.";
            }
        } else {
            echo "Invalid file type or file size exceeds limit.";
        }
    }
    return null;
}

// Check if the current user is an admin
function is_admin() {
    return isset($_SESSION['user_role']) && $_SESSION['user_role'] === 'admin';
}

// Determine page route from the URL
$page = isset($_GET['page']) ? $_GET['page'] : 'home';

// Handle POST request actions safely
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if ($page === 'register') {
        $username = sanitize($_POST['username']);
        $password = sanitize($_POST['password']);
        $bio = sanitize($_POST['bio']);
        $avatar = handle_avatar_upload();
        if (!empty($username) && strlen($username) >= 5 && !empty($password) && strlen($password) >= 8) {
            $hashedPassword = password_hash($password, PASSWORD_BCRYPT);
            $stmt = $pdo->prepare("INSERT INTO users (username, password, bio, avatar) VALUES (?, ?, ?, ?)");
            if ($stmt->execute([$username, $hashedPassword, $bio, $avatar])) {
                echo "User registered successfully!";
            } else {
                echo "Error during registration.";
            }
        } else {
            echo "Invalid input. Username must be at least 5 characters and password at least 8 characters.";
        }
    } elseif ($page === 'login') {
        $username = sanitize($_POST['username']);
        $password = sanitize($_POST['password']);
        $stmt = $pdo->prepare("SELECT * FROM users WHERE username = ?");
        $stmt->execute([$username]);
        $user = $stmt->fetch();
        if ($user && password_verify($password, $user['password'])) {
            session_regenerate_id(true);
            $_SESSION['user_id'] = $user['id'];
            $_SESSION['username'] = $user['username'];
            $_SESSION['user_role'] = $user['role']; // assumes 'role' field exists
            header('Location: index.php?page=forum');
        } else {
            echo "Invalid credentials.";
        }
    } elseif (isset($_SESSION['user_id']) && $page === 'update_bio') {
        $bio = sanitize($_POST['bio']);
        $avatar = handle_avatar_upload();
        $stmt = $pdo->prepare("UPDATE users SET bio = ?, avatar = ? WHERE id = ?");
        if ($stmt->execute([$bio, $avatar ?? $user_profile['avatar'], $_SESSION['user_id']])) {
            echo "Profile updated successfully!";
        } else {
            echo "Error updating profile.";
        }
    } elseif (isset($_SESSION['user_id']) && $page === 'post_message') {
        $message = sanitize($_POST['message']);
        if (!empty($message)) {
            $stmt = $pdo->prepare("INSERT INTO messages (user_id, content) VALUES (?, ?)");
            if ($stmt->execute([$_SESSION['user_id'], $message])) {
                echo "Message posted!";
            } else {
                echo "Error posting message.";
            }
        } else {
            echo "Message cannot be empty.";
        }
    } elseif (isset($_SESSION['user_id']) && $page === 'reply_message') {
        $reply = sanitize($_POST['reply']);
        $parent_id = intval($_POST['parent_id']);
        if (!empty($reply)) {
            $stmt = $pdo->prepare("INSERT INTO messages (user_id, content, parent_id) VALUES (?, ?, ?)");
            if ($stmt->execute([$_SESSION['user_id'], $reply, $parent_id])) {
                echo "Reply posted!";
            } else {
                echo "Error posting reply.";
            }
        } else {
            echo "Reply cannot be empty.";
        }
    } elseif (is_admin() && $page === 'moderate') {
        $action = sanitize($_POST['action']);
        $message_id = intval($_POST['message_id']);
        if ($action === 'edit') {
            $new_content = sanitize($_POST['new_content']);
            $stmt = $pdo->prepare("UPDATE messages SET content = ? WHERE id = ?");
            if ($stmt->execute([$new_content, $message_id])) {
                echo "Message edited successfully!";
            } else {
                echo "Error editing message.";
            }
        } elseif ($action === 'delete') {
            $stmt = $pdo->prepare("DELETE FROM messages WHERE id = ?");
            if ($stmt->execute([$message_id])) {
                echo "Message deleted successfully!";
            } else {
                echo "Error deleting message.";
            }
        }
    }
}

// Retrieve user profile information
$user_profile = [];
if (isset($_GET['user_id'])) {
    $user_id = intval($_GET['user_id']);
    $stmt = $pdo->prepare("SELECT username, bio, avatar FROM users WHERE id = ?");
    $stmt->execute([$user_id]);
    $user_profile = $stmt->fetch();
}

// Execute search based on keyword
$search_results = [];
if ($_SERVER['REQUEST_METHOD'] == 'GET' && $page === 'search') {
    if (isset($_GET['keyword'])) {
        $keyword = sanitize($_GET['keyword']);
        $stmt = $pdo->prepare("SELECT * FROM messages WHERE content LIKE ?");
        $stmt->execute(['%' . $keyword . '%']);
        $search_results = $stmt->fetchAll();
    }
}

// Determine which page to render
include 'header.php';

switch ($page) {
    case 'home':
        include 'home.php';
        break;
    case 'register':
        include 'register.php';
        break;
    case 'login':
        include 'login.php';
        break;
    case 'forum':
        include 'forum.php';
        break;
    case 'profile':
        include 'profile.php';
        break;
    case 'search':
        include 'search.php';
        break;
    case 'admin':
        if (is_admin()) {
            include 'admin.php';
        } else {
            echo "Access denied.";
        }
        break;
    default:
        echo "Page not found.";
        break;
}

include 'footer.php';
?>

<!-- Admin moderation page for editing/deleting messages -->
<!-- admin.php -->
<h2>Admin Moderation Page</h2>
<?php
if (is_admin()) {
    $messages = $pdo->query("SELECT * FROM messages")->fetchAll();
    foreach ($messages as $message) {
        echo "<div>" . safe_output($message['content']) . " by User ID: " . safe_output($message['user_id']) . "</div>";
        echo '<form action="index.php?page=moderate" method="POST">
                <input type="hidden" name="message_id" value="' . intval($message['id']) . '">
                <textarea name="new_content">' . safe_output($message['content']) . '</textarea>
                <button type="submit" name="action" value="edit">Edit</button>
                <button type="submit" name="action" value="delete">Delete</button>
              </form>';
    }
} else {
    echo "Access denied.";
}
?>
