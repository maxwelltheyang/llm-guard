<?php
session_start();
$dsn = 'mysql:host=localhost;dbname=forum';
$username = 'root'; // Change as needed
$password = ''; // Change as needed
$options = [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION];

$pdo = new PDO($dsn, $username, $password, $options);

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['register'])) {
        $stmt = $pdo->prepare('INSERT INTO users (username, password) VALUES (?, ?)');
        $stmt->execute([$_POST['username'], password_hash($_POST['password'], PASSWORD_BCRYPT)]);
    } elseif (isset($_POST['login'])) {
        $stmt = $pdo->prepare('SELECT * FROM users WHERE username = ?');
        $stmt->execute([$_POST['username']]);
        $user = $stmt->fetch();
        if ($user && password_verify($_POST['password'], $user['password'])) {
            $_SESSION['user_id'] = $user['id'];
        }
    } elseif (isset($_POST['post'])) {
        $stmt = $pdo->prepare('INSERT INTO posts (user_id, content) VALUES (?, ?)');
        $stmt->execute([$_SESSION['user_id'], $_POST['content']]);
    } elseif (isset($_POST['reply'])) {
        $stmt = $pdo->prepare('INSERT INTO replies (post_id, user_id, content) VALUES (?, ?, ?)');
        $stmt->execute([$_POST['post_id'], $_SESSION['user_id'], $_POST['content']]);
    }
}

$posts = $pdo->query('SELECT posts.*, users.username FROM posts JOIN users ON posts.user_id = users.id')->fetchAll();

?>

<!DOCTYPE html>
<html>
<head>
    <title>Forum</title>
</head>
<body>

<?php if (!isset($_SESSION['user_id'])): ?>

<h2>Register</h2>
<form method="post">
    <input type="text" name="username" placeholder="Username" required>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit" name="register">Register</button>
</form>

<h2>Login</h2>
<form method="post">
    <input type="text" name="username" placeholder="Username" required>
    <input type="password" name="password" placeholder="Password" required>
    <button type="submit" name="login">Login</button>
</form>

<?php else: ?>

<h2>Post a Message</h2>
<form method="post">
    <textarea name="content" placeholder="Your message" required></textarea>
    <button type="submit" name="post">Post</button>
</form>

<h2>Messages</h2>
<?php foreach ($posts as $post): ?>
    <div>
        <strong><?php echo htmlspecialchars($post['username']); ?>:</strong>
        <p><?php echo htmlspecialchars($post['content']); ?></p>
        <h3>Replies</h3>
        <?php
        $stmt = $pdo->prepare('SELECT replies.*, users.username FROM replies JOIN users ON replies.user_id = users.id WHERE post_id = ?');
        $stmt->execute([$post['id']]);
        $replies = $stmt->fetchAll();
        foreach ($replies as $reply): ?>
            <div>
                <strong><?php echo htmlspecialchars($reply['username']); ?>:</strong>
                <p><?php echo htmlspecialchars($reply['content']); ?></p>
            </div>
        <?php endforeach; ?>
        <form method="post">
            <textarea name="content" placeholder="Your reply" required></textarea>
            <input type="hidden" name="post_id" value="<?php echo $post['id']; ?>">
            <button type="submit" name="reply">Reply</button>
        </form>
    </div>
<?php endforeach; ?>

<?php endif; ?>

</body>
</html>
