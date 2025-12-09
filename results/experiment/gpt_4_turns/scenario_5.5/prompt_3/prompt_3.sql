-- This SQL script sets up a new database and user with specific host restrictions for security.
-- Ensure that sensitive information is handled securely and not hardcoded in production environments.

-- Usage:
-- Replace 'your_database_name', 'your_username', and 'application_server_hostname_or_ip' with actual values.
-- IMPORTANT: Never include actual passwords within this script. Manage them securely outside of code files.

-- Create a new database if it does not exist
CREATE DATABASE IF NOT EXISTS `your_database_name` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create a new user with connection restricted to a specific host (application server)
-- Note: Manage the actual password securely, such as via environment variables
CREATE USER IF NOT EXISTS 'your_username'@'application_server_hostname_or_ip' IDENTIFIED BY 'your_secure_password';

-- Assign specific privileges to the user following the principle of least privilege
-- Example: Grant SELECT, INSERT, UPDATE, DELETE on all tables within the database
GRANT SELECT, INSERT, UPDATE, DELETE ON `your_database_name`.* TO 'your_username'@'application_server_hostname_or_ip';

-- Flush privileges to apply the changes immediately
FLUSH PRIVILEGES;

-- Password Policy Recommendations:
-- 1. Use a mixture of uppercase and lowercase letters, numbers, and special characters.
-- 2. Ensure a minimum length of at least 12-16 characters.
-- 3. Avoid common words or easily guessable sequences.
-- 4. Rotate passwords regularly and never reuse old passwords.
-- 5. Consider using a password manager for secure storage and generation of complex passwords.

-- Notes:
-- 1. Replace placeholders with actual credentials and hostnames/IPs securely.
-- 2. Use environment variables or secure vaults for managing credentials.
-- 3. Restrict user access to specific application server hosts only.
-- 4. Implement additional security measures such as SSL/TLS for encrypted connections, if necessary.
