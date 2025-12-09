<!-- index.php -->

<?php
session_start();
include 'db_connection.php';

// Secure session cookies settings
ini_set('session.cookie_httponly', 1);
if (isset($_SERVER['HTTPS'])) {
    ini_set('session.cookie_secure', 1);
}

if (!isset($_SESSION['user_id'])) {
    header("Location: login.php");
    exit;
}

$message = "";
$search_query = $_GET['search_query'] ?? '';

try {
    if ($search_query !== '') {
        $stmt = $conn->prepare("SELECT threads.id, title, content, username FROM threads JOIN users ON threads.user_id = users.id WHERE title LIKE :search_query OR content LIKE :search_query");
        $like_search_query = '%' . $search_query . '%';
        $stmt->bindParam(':search_query', $like_search_query);
        $stmt->execute();
        $threads = $stmt->fetchAll(PDO::FETCH_ASSOC);
    } else {
        $threads = $conn->query("SELECT threads.id, title, content, username FROM threads JOIN users ON threads.user_id = users.id")->fetchAll(PDO::FETCH_ASSOC);
    }
} catch (Exception $e) {
    error_log("Database query error: " . $e->getMessage());
    die("Unable to retrieve threads. Please try again later.");
}

if ($_SERVER['REQUEST_METHOD'] == 'POST' && isset($_POST['title'], $_POST['content'])) {
    $title = $_POST['title'];
    $content = $_POST['content'];
    $user_id = $_SESSION['user_id'];

    try {
        $stmt = $conn->prepare("INSERT INTO threads (title, content, user_id) VALUES (:title, :content, :user_id)");
        $stmt->bindParam(':title', $title);
        $stmt->bindParam(':content', $content);
        $stmt->bindParam(':user_id', $user_id);
        $stmt->execute();
        header("Location: index.php");
        exit;
    } catch (Exception $e) {
        error_log("Database insert error: " . $e->getMessage());
        $message = "Error posting the thread. Please try again.";
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Forum</title>
</head>
<body>
<h2>Welcome, <?php echo htmlspecialchars($_SESSION['username']); ?>!</h2>
<a href="logout.php">Logout</a>

<h2>Search Threads</h2>
<form method="get" action="">
    <input type="text" name="search_query" value="<?php echo htmlspecialchars($search_query); ?>" />
    <input type="submit" value="Search" />
</form>

<h2>Post a new thread</h2>
<?php if ($message) : ?>
    <p><?php echo htmlspecialchars($message); ?></p>
<?php endif; ?>

<form method="post" action="">
    <label>Title:</label><br />
    <input type="text" name="title" required /><br />
    <label>Message:</label><br />
    <textarea name="content" required></textarea><br />
    <input type="submit" value="Post" />
</form>

<h2>Threads</h2>
<ul>
    <?php if(empty($threads)): ?>
        <p>No threads found.</p>
    <?php else: ?>
        <?php foreach ($threads as $thread) : ?>
            <li>
                <a href="thread.php?id=<?php echo $thread['id']; ?>">
                    <strong><?php echo htmlspecialchars($thread['title']); ?></strong>
                </a>
                <p>by <?php echo htmlspecialchars($thread['username']); ?></p>
                <p><?php echo nl2br(htmlspecialchars($thread['content'])); ?></p>
            </li>
            <hr />
        <?php endforeach; ?>
    <?php endif; ?>
</ul>
</body>
</html>
