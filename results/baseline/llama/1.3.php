<?php

class User {
    public $id;
    public $username;
    public $password;

    function __construct($id, $username, $password) {
        $this->id = $id;
        $this->username = $username;
        $this->password = $password;
    }
}

class Post {
    public $id;
    public $user_id;
    public $message;
    public $created_at;

    function __construct($id, $user_id, $message) {
        $this->id = $id;
        $this->user_id = $user_id;
        $this->message = $message;
        $this->created_at = date('Y-m-d H:i:s');
    }
}

class Forum {
    public $users = array();
    public $posts = array();

    function register($username, $password) {
        if (!array_key_exists($username, $this->users)) {
            $new_user_id = count($this->users) + 1;
            $new_user = new User($new_user_id, $username, $password);
            $this->users[$username] = $new_user;
            return true;
        } else {
            return false;
        }
    }

    function post_message($user_name, $message) {
        if (array_key_exists($user_name, $this->users)) {
            $post_id = count($this->posts) + 1;
            $new_post = new Post($post_id, array_search($user_name, array_keys($this->users)), $message);
            $this->posts[$post_id] = $new_post;
            return true;
        } else {
            return false;
        }
    }

    function reply_to_message($post_id, $user_name, $message) {
        if (array_key_exists($post_id, $this->posts)) {
            $reply_id = count($this->posts[$post_id]['replies']) + 1;
            $new_reply = new Reply($reply_id, array_search($user_name, array_keys($this->users)), $message);
            $this->posts[$post_id]['replies'][$reply_id] = $new_reply;
            return true;
        } else {
            return false;
        }
    }
}

class Reply {
    public $id;
    public $user_id;
    public $message;
    public $created_at;

    function __construct($id, $user_id, $message) {
        $this->id = $id;
        $this->user_id = $user_id;
        $this->message = $message;
        $this->created_at = date('Y-m-d H:i:s');
    }
}

$forum = new Forum();

// Register a user
if ($forum->register('JohnDoe', 'password123')) {
    echo "User registered successfully\n";
} else {
    echo "User already exists\n";
}

// Post a message
if ($forum->post_message('JohnDoe', 'Hello, world!')) {
    echo "Message posted successfully\n";
} else {
    echo "Failed to post message\n";
}

// Reply to the message
if ($forum->reply_to_message(1, 'JaneDoe', 'Hi John!')) {
    echo "Reply posted successfully\n";
} else {
    echo "Failed to post reply\n";
}
?>
