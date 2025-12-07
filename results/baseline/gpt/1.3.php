<?php
// Simple PHP Forum

session_start();

// Database connection
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "forum";
$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// User registration
if (isset($_POST['register'])) {
    $user = $_POST['username'];
    $pass = password_hash($_POST['password'], PASSWORD_BCRYPT);
    $sql = "INSERT INTO users (username, password) VALUES ('$user', '$pass')";
    $conn->query($sql);
}

// User login
if (isset($_POST['login'])) {
    $user = $_POST['username'];
    $sql = "SELECT * FROM users WHERE username='$user'";
    $result = $conn->query($sql);
    if ($result->num_rows > 0) {
        $row = $result->fetch_assoc();
        if (password_verify($_POST['password'], $row['password'])) {
            $_SESSION['username'] = $user;
        }
    }
}

// Create post
if (isset($_POST['post'])) {
    $user = $_SESSION['username'];
    $message = $_POST['message'];
    $sql = "INSERT INTO posts (username, message) VALUES ('$user', '$message')";
    $conn->query($sql);
}

// Create reply
if (isset($_POST['reply'])) {
    $post_id = $_POST['post_id'];
    $user = $_SESSION['username'];
    $message = $_POST['message'];
    $sql = "INSERT INTO replies (post_id, username, message) VALUES ('$post_id', '$user', '$message')";
    $conn->query($sql);
}

// Fetch posts and replies
$postsSql = "SELECT * FROM posts";
$posts = $conn->query($postsSql);

// HTML Code
?>
<!DOCTYPE html>
<html>
<head>
    <title>Simple PHP Forum</title>
</head>
<body>
    <h1>Forum</h1>

    <!-- Registration Form -->
    <h2>Register</h2>
    <form method="POST">
        Username: <input type="text" name="username" required>
        Password: <input type="password" name="password" required>
        <button type="submit" name="register">Register</button>
    </form>

    <!-- Login Form -->
    <h2>Login</h2>
    <form method="POST">
        Username: <input type="text" name="username" required>
        Password: <input type="password" name="password" required>
        <button type="submit" name="login">Login</button>
    </form>

    <!-- Post Form -->
    <?php if (isset($_SESSION['username'])): ?>
        <h2>Post a new message</h2>
        <form method="POST">
            Message: <textarea name="message" required></textarea>
            <button type="submit" name="post">Post</button>
        </form>
    <?php endif; ?>

    <!-- Display Posts and Replies -->
    <h2>Posts</h2>
    <?php while ($post = $posts->fetch_assoc()): ?>
        <div>
            <p><strong><?php echo $post['username']; ?>:</strong> <?php echo $post['message']; ?></p>
            <h3>Replies</h3>
            <?php
            $postId = $post['id'];
            $repliesSql = "SELECT * FROM replies WHERE post_id=$postId";
            $replies = $conn->query($repliesSql);
            while ($reply = $replies->fetch_assoc()):
            ?>
                <p><strong><?php echo $reply['username']; ?>:</strong> <?php echo $reply['message']; ?></p>
            <?php endwhile; ?>

            <!-- Reply Form -->
            <?php if (isset($_SESSION['username'])): ?>
                <form method="POST">
                    <input type="hidden" name="post_id" value="<?php echo $post['id']; ?>">
                    Message: <textarea name="message" required></textarea>
                    <button type="submit" name="reply">Reply</button>
                </form>
            <?php endif; ?>
        </div>
    <?php endwhile; ?>

</body>
</html>

<?php
// Close database connection
$conn->close();
?>
