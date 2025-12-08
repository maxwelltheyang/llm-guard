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

class Message {
    public $id;
    public $content;
    public $author_id;
    public $parent_message_id;

    function __construct($id, $content, $author_id) {
        $this->id = $id;
        $this->content = $content;
        $this->author_id = $author_id;
        $this->parent_message_id = null;
    }
}

class Forum {
    public $users = array();
    public $messages = array();

    function register($username, $password) {
        if (!isset($this->users[$username])) {
            $new_user = new User(count($this->users), $username, $password);
            $this->users[$username] = $new_user;
            return true;
        } else {
            return false;
        }
    }

    function login($username, $password) {
        if (isset($this->users[$username]) && $this->users[$username]->password == $password) {
            return $this->users[$username];
        } else {
            return null;
        }
    }

    function post_message($content, $author_id) {
        $new_message = new Message(count($this->messages), $content, $author_id);
        $this->messages[count($this->messages)] = $new_message;
        return count($this->messages) - 1;
    }

    function reply_to_message($parent_id, $content, $author_id) {
        if (isset($this->messages[$parent_id])) {
            $new_message = new Message(count($this->messages), $content, $author_id);
            $new_message->parent_message_id = $parent_id;
            $this->messages[count($this->messages)] = $new_message;
            return count($this->messages) - 1;
        } else {
            return null;
        }
    }

    function get_messages() {
        return $this->messages;
    }
}

$forum = new Forum();

echo "Register user:\n";
$forum->register("JohnDoe", "password123");
print_r($forum->users);

echo "\nLogin user:\n";
$user = $forum->login("JohnDoe", "password123");
print_r($user);

echo "\nPost message:\n";
$message_id1 = $forum->post_message("Hello, world!", 1);
echo $message_id1 . "\n";

echo "\nReply to message:\n";
$message_id2 = $forum->reply_to_message(1, "Hi there!", 1);
echo $message_id2 . "\n";

echo "\nGet all messages:\n";
print_r($forum->get_messages());

?>
