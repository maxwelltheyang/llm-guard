-- This SQL script sets up a new database and user with best practices for security in mind.
-- Ensure that sensitive information is handled securely and not hardcoded in production environments.

-- Usage:
-- Replace 'your_database_name', 'your_username', and 'your_secure_password' with actual values.

-- Create a new database if it does not exist
CREATE DATABASE IF NOT EXISTS `your_database_name` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create a new user only if the user does not already exist
CREATE USER IF NOT EXISTS 'your_username'@'localhost' IDENTIFIED BY 'your_secure_password';

-- Assign specific privileges to the user following the principle of least privilege
-- Example: Grant SELECT, INSERT, UPDATE, DELETE on all tables within the database
GRANT SELECT, INSERT, UPDATE, DELETE ON `your_database_name`.* TO 'your_username'@'localhost';

-- Flush privileges to apply the changes immediately
FLUSH PRIVILEGES;

-- Notes:
-- 1. Replace placeholders with actual credentials securely.
-- 2. Use strong, complex passwords and rotate them regularly.
-- 3. Consider using environment variables or secure vaults for managing credentials.
-- 4. Restrict user access to specific hosts as needed. Default setup is for localhost only.
-- 5. Implement additional security measures such as SSL/TLS for encrypted connections, if necessary.
