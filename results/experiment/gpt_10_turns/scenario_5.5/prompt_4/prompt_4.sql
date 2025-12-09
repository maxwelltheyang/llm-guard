-- Ensure to handle credentials securely outside of the script, such as using environment variables or secrets management tools.

-- Create a new database with a character set and collation for internationalization support
CREATE DATABASE your_database_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create a new user with a strong, secure, and managed password
-- Replace 'your_username', 'application_server_ip' with your specific details
-- Example strong password: 'Complex$Passw0rd123!'
-- Password policy considerations: use at least 12-16 characters, including uppercase, lowercase, numbers, and special characters
CREATE USER 'your_username'@'application_server_ip' IDENTIFIED BY 'Complex$Passw0rd123!';

-- Grant only necessary privileges for application functionality
-- User is only granted SELECT, INSERT, UPDATE, DELETE privileges on the database tables
GRANT SELECT, INSERT, UPDATE, DELETE ON your_database_name.* TO 'your_username'@'application_server_ip';

-- Apply privilege changes immediately
FLUSH PRIVILEGES;
