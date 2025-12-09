-- Create a new database
CREATE DATABASE IF NOT EXISTS my_application_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create a new user with a strong password fetched from an environment variable
-- Note: Set the environment variable before running this snippet, or use a credential management system
-- Make sure to replace 'localhost' with the specific application server host if different
CREATE USER IF NOT EXISTS 'my_app_user'@'localhost' IDENTIFIED BY 'ENV_MY_APP_PASSWORD' REQUIRE SSL;

-- Replace 'ENV_MY_APP_PASSWORD' with the actual environment variable or use a password vault mechanism
-- Example password policy: At least 12 characters, including uppercase, lowercase, numbers, and symbols
-- Example in shell: export ENV_MY_APP_PASSWORD='Str0ng!Passw0rd#123'

-- Grant only necessary privileges (SELECT, INSERT, UPDATE, DELETE) to the new user for the new database
GRANT SELECT, INSERT, UPDATE, DELETE ON my_application_db.* TO 'my_app_user'@'localhost';

-- Ensure the privileges are reloaded and applied
FLUSH PRIVILEGES;

-- Additional security recommendations:
-- 1. Regularly review and update user privileges. Periodically audit database permissions to ensure no unneeded permissions.
-- 2. Enable logging and monitoring of database access and queries for security audits.
-- 3. Regularly update MySQL to the latest version to protect against vulnerabilities.
-- 4. Backup data securely and ensure backups are encrypted.
-- 5. Limit user access to specific IP addresses by using a firewall to block unauthorized access.
-- 6. Employ database-specific security features such as MySQL's 'validate_password' plugin to enforce stronger password policies.
-- 7. Set up a dedicated network segment for database servers separate from application servers.
-- 8. Consider using MySQL's built-in encryption functions for sensitive data.
