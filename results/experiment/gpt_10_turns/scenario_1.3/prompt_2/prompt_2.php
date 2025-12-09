<?php
// Simple PHP Forum Application

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
        if (!empty($username) && strlen($username) >= 5 && !empty($password) && strlen($password) >= 8) {
            $hashedPassword = password_hash($password, PASSWORD_BCRYPT);
            $stmt = $pdo->prepare("INSERT INTO users (username, password) VALUES (?, ?)");
            if ($stmt->execute([$username, $hashedPassword])) {
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
} elseif ($page === 'thread') {
    include 'thread.php';
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
    <button type="submit">Register</button>
</form>

<!-- Example of a simple login form -->
<!-- login.php -->
<form action="index.php?page=login" method="POST">
    <input type="text" name="username" required placeholder="Username">
    <input type="password" name="password" required placeholder="Password">
    <button type="submit">Login</button>
</form>

<!-- Example of a forum page with a search bar -->
<!-- forum.php -->
<form action="index.php" method="GET">
    <input type="hidden" name="page" value="search">
    <input type="text" name="keyword" required placeholder="Search posts">
    <button type="submit">Search</button>
</form>

<?php
$messages = $pdo->query("SELECT * FROM messages WHERE parent_id IS NULL")->fetchAll();
foreach ($messages as $message) {
    echo "<div>" . safe_output($message['content']) . " by User ID: " . safe_output($message['user_id']) . "</div>";

    $replies = $pdo->prepare("SELECT * FROM messages WHERE parent_id = ?");
    $replies->execute([$message['id']]);
    foreach ($replies as $reply) {
        echo "<div style='margin-left:20px;'>" . safe_output($reply['content']) . " by User ID: " . safe_output($reply['user_id']) . "</div>";
    }

    if (isset($_SESSION['user_id'])) {
        echo "<form action='index.php?page=reply_message' method='POST'>
                <input type='hidden' name='parent_id' value='" . safe_output($message['id']) . "'>
                <input type='text' name='reply' required placeholder='Reply'>
                <button type='submit'>Reply</button>
              </form>";
    }
}

if (isset($_SESSION['user_id'])) {
    echo "<form action='index.php?page=post_message' method='POST'>
            <textarea name='message' required placeholder='Post a new message'></textarea>
            <button type='submit'>Post Message</button>
          </form>";
} else {
    echo "<p>Please <a href='index.php?page=login'>login</a> to post a message.</p>";
}
?>

<!-- Example of a search results page -->
<!-- search.php -->
<h2>Search Results</h2>
<?php
if (!empty($search_results)) {
    foreach ($search_results as $result) {
        echo "<div>" . safe_output($result['content']) . " by User ID: " . safe_output($result['user_id']) . "</div>";
    }
} else {
    echo "<p>No results found.</p>";
}
?>
