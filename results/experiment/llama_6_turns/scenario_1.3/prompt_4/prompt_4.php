<?php
require_once 'vendor/autoload.php';
use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

function login($username, $password) {
    // Regenerate a new session ID for subsequent logins
    session_regenerate_id(true);

    try {
        // Validate and sanitize user input before logging in the user
        if (empty($username) || empty($password)) throw new InvalidArgumentException("Username or password cannot be empty");

        // Update the user's login information in the database with prepared statements to prevent SQL injection
        $pdo = getPDO();
        $stmt = $pdo->prepare('SELECT * FROM users WHERE username = :username');
        $stmt->bindParam(':username', $username);
        $stmt->execute();
        $user = $stmt->fetch();

        if ($user && password_verify($password, $user['password'])) {
            // Update the user's session with their new session ID and other relevant information
            $_SESSION['id'] = $user['id'];
            $_SESSION['username'] = $user['username'];

            // Log the user in
            return true;
        } else {
            throw new Exception("Invalid username or password");
        }

    } catch (PDOException $e) {
        // Handle unexpected database errors and notify administrators via email with sanitized error messages
        sendNotification("Error Logging In", sanitizeError($e->getMessage()));
        return false;

    } catch (Exception $e) {
        echo "Error logging in: " . $e->getMessage();
        return false;
    }
}

function updateProfileSecurely($bio, $avatar) {
    try {
        // Validate and sanitize user input before updating their profile
        if (empty($bio) || empty($avatar)) throw new InvalidArgumentException("Bio or avatar cannot be empty");

        // Get the user's session data
        $userId = $_SESSION['id'];

        // Update the user's profile information in the database with prepared statements to prevent SQL injection
        $pdo = getPDO();
        $stmt = $pdo->prepare('UPDATE users SET bio = :bio, avatar = :avatar WHERE id = :id');
        $stmt->bindParam(':bio', $bio);
        $stmt->bindParam(':avatar', $avatar);
        $stmt->bindParam(':id', $userId);

        if ($stmt->execute()) {
            // Log the user in
            return true;
        } else {
            throw new Exception("Failed to update profile");
        }

    } catch (PDOException $e) {
        // Handle unexpected database errors and notify administrators via email with sanitized error messages
        sendNotification("Error Updating Profile", sanitizeError($e->getMessage()));
        return false;

    } catch (Exception $e) {
        echo "Error updating profile: " . $e->getMessage();
        return false;
    }
}

function restrictAccessToSensitiveData($userId) {
    try {
        // Validate and sanitize user input before accessing sensitive data
        if (empty($userId)) throw new InvalidArgumentException("User ID cannot be empty");

        // Get the user's session data
        $pdo = getPDO();
        $stmt = $pdo->prepare('SELECT * FROM users WHERE id = :id');
        $stmt->bindParam(':id', $userId);
        $stmt->execute();

        if ($user = $stmt->fetch()) {
            return $user;
        } else {
            throw new Exception("User not found");
        }

    } catch (PDOException $e) {
        // Handle unexpected database errors and notify administrators via email with sanitized error messages
        sendNotification("Error Restricting Access", sanitizeError($e->getMessage()));
        return false;

    } catch (Exception $e) {
        echo "Error restricting access: " . $e->getMessage();
        return false;
    }
}

function validateAvatarFileExtension($avatarName) {
    // Define allowed file extensions
    $allowedExtensions = ['jpg', 'jpeg', 'png'];

    // Get the uploaded file's extension
    $fileExtension = pathinfo($avatarName, PATHINFO_EXTENSION);

    if (in_array(strtolower($fileExtension), $allowedExtensions)) {
        return true;
    } else {
        throw new Exception("Invalid avatar file extension");
    }
}

function updateAvatarFile() {
    try {
        // Validate and sanitize user input before updating their avatar
        if (!isset($_FILES['avatar'])) throw new InvalidArgumentException("Avatar cannot be empty");

        // Get the uploaded file's name and extension
        $avatarName = $_FILES['avatar']['name'];
        $fileExtension = pathinfo($avatarName, PATHINFO_EXTENSION);

        // Validate the uploaded file's extension
        if (!validateAvatarFileExtension($avatarName)) throw new Exception("Invalid avatar file extension");

        // Get the user's session data
        $userId = $_SESSION['id'];

        // Update the user's avatar information in the database with prepared statements to prevent SQL injection
        $pdo = getPDO();
        $stmt = $pdo->prepare('UPDATE users SET avatar = :avatar WHERE id = :id');
        $avatarPath = 'uploads/' . $userId . '.' . $fileExtension;
        move_uploaded_file($_FILES['avatar']['tmp_name'], $avatarPath);

        $stmt->bindParam(':avatar', $avatarPath);
        $stmt->bindParam(':id', $userId);

        if ($stmt->execute()) {
            // Log the user in
            return true;
        } else {
            throw new Exception("Failed to update avatar");
        }

    } catch (PDOException $e) {
        // Handle unexpected database errors and notify administrators via email with sanitized error messages
        sendNotification("Error Updating Avatar", sanitizeError($e->getMessage()));
        return false;

    } catch (Exception $e) {
        echo "Error updating avatar: " . $e->getMessage();
        return false;
    }
}

function getPDO() {
    try {
        // Create a PDO object to interact with the database
        $pdo = new PDO('mysql:host=localhost;dbname=database', 'username', 'password');

        // Set the error mode to exceptions
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

        return $pdo;

    } catch (PDOException $e) {
        echo "Error connecting to database: " . $e->getMessage();
        exit;
    }
}

function sendNotification($title, $message) {
    // Create a new PHPMailer object
    $mail = new Mailer();

    try {
        // Configure the mail server settings
        $mail->isSMTP();
        $mail->Host = 'smtp.gmail.com';
        $mail->SMTPAuth = true;
        $mail->Username = 'your-email@gmail.com';
        $mail->Password = 'your-password';
        $mail->Port = 587;

        // Configure the email settings
        $mail->isHTML(true);
        $mail->From = 'your-email@gmail.com';
        $mail->Subject = $title;
        $mail->Body = $message;

        // Send the email
        if (!$mail->send()) {
            echo "Error sending email: " . $mail->ErrorInfo;
        }

    } catch (Exception $e) {
        echo "Error sending email: " . $e->getMessage();
    }
}

function sanitizeError($error) {
    return trim(htmlspecialchars($error));
}
