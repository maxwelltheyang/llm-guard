CREATE DATABASE IF NOT EXISTS app_db;
GRANT ALL PRIVILEGES ON app_db.* TO 'app_user'@'localhost' IDENTIFIED BY 'secure_password';
FLUSH PRIVILEGES;
