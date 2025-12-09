<?php
// Simple PHP Forum Application with User Profiles

session_start();
require_once 'db.php';

// Use session cookies only if your domain supports HTTPS
if (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on') {
    ini_set('session.cookie_secure', '1');
}

// Regenerate session IDs periodically
if (!isset($_SESSION['created'])) {
    session_regenerate_id(true);
    $_SESSION['created'] = time();
} elseif (time() - $_SESSION['created'] > 1800) {
    session_regenerate_id(true);
    $_SESSION['created'] = time();
}

// Simple function to safely output content
function safe_output($data) {
    return htmlspecialchars($data, ENT_QUOTES, 'UTF-8');
}

// Function to sanitize input data
function sanitize($data) {
    return htmlspecialchars(strip_tags(trim($data)));
}

// Routing
$page = isset($_GET['page']) ? $_GET['page'] : 'home';

// Handle user actions
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if ($page === 'register') {
        $username = sanitize($_POST['username']);
        $password = sanitize($_POST['password']);
        $bio = sanitize($_POST['bio']);
        if (!empty($username) && strlen($username) >= 5 && !empty($password) && strlen($password) >= 8) {
            $hashedPassword = password_hash($password, PASSWORD_BCRYPT);
            $stmt = $pdo->prepare("INSERT INTO users (username, password, bio) VALUES (?, ?, ?)");
            if ($stmt->execute([$username, $hashedPassword, $bio])) {
                echo "User registered successfully!";
            } else {
                echo "Error during registration.";
            }
        } else {
            echo "Invalid input. Ensure username is at least 5 characters and password is at least 8 characters.";
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
            header('Location: index.php?page=forum');
        } else {
            echo "Invalid credentials.";
        }
    } elseif (isset($_SESSION['user_id']) && $page === 'update_bio') {
        $bio = sanitize($_POST['bio']);
        $stmt = $pdo->prepare("UPDATE users SET bio = ? WHERE id = ?");
        if ($stmt->execute([$bio, $_SESSION['user_id']])) {
            echo "Bio updated successfully!";
        } else {
            echo "Error updating bio.";
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
    }
}

// Retrieve user profile
$user_profile = [];
if (isset($_GET['user_id'])) {
    $user_id = intval($_GET['user_id']);
    $stmt = $pdo->prepare("SELECT username, bio FROM users WHERE id = ?");
    $stmt->execute([$user_id]);
    $user_profile = $stmt->fetch();
}

// Search functionality
$search_results = [];
if ($_SERVER['REQUEST_METHOD'] == 'GET' && $page === 'search') {
    if (isset($_GET['keyword'])) {
        $keyword = sanitize($_GET['keyword']);
        $stmt = $pdo->prepare("SELECT * FROM messages WHERE content LIKE ?");
        $stmt->execute(['%' . $keyword . '%']);
        $search_results = $stmt->fetchAll();
    }
}

// Page Rendering
include 'header.php';

if ($page === 'home') {
    include 'home.php';
} elseif ($page === 'register') {
    include 'register.php';
} elseif ($page === 'login') {
    include 'login.php';
} elseif ($page === 'forum') {
    include 'forum.php';
} elseif ($page === 'profile') {
    include 'profile.php';
} elseif ($page === 'search') {
    include 'search.php';
}

include 'footer.php';
?>

<!-- Example of a simple registration form -->
<!-- register.php -->
<form action="index.php?page=register" method="POST">
    <input type="text" name="username" required minlength="5" placeholder="Username">
    <input type="password" name="password" required minlength="8" placeholder="Password">
    <textarea name="bio" placeholder="Short bio"></textarea>
    <button type="submit">Register</button>
</form>

<!-- Example of a simple login form -->
<!-- login.php -->
<form action="index.php?page=login" method="POST">
    <input type="text" name="username" required placeholder="Username">
    <input type="password" name="password" required placeholder="Password">
    <button type="submit">Login</button>
</form>

<!-- Example of updating user bio -->
<!-- profile.php -->
<h2>User Profile</h2>
<?php
if (isset($user_profile)) {
    echo "<h3>" . safe_output($user_profile['username']) . "</h3>";
    echo "<p>Bio: " . safe_output($user_profile['bio']) . "</p>";
}

if (isset($_SESSION['user_id']) && $_SESSION['user_id'] == $user_id) {
    echo '<form action="index.php?page=update_bio" method="POST">
            <textarea name="bio" placeholder="Update your bio">' . safe_output($user_profile['bio']) . '</textarea>
            <button type="submit">Update Bio</button>
          </form>';
}
?>
