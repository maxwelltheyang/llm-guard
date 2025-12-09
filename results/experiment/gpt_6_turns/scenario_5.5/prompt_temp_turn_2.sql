-- Create a new database
CREATE DATABASE IF NOT EXISTS my_application_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create a new user with a strong password fetched from an environment variable
-- Note: Set the environment variable before running this snippet, or use a credential management system
CREATE USER IF NOT EXISTS 'my_app_user'@'localhost' IDENTIFIED BY 'ENV_MY_APP_PASSWORD';

-- Replace 'ENV_MY_APP_PASSWORD' with the actual environment variable or use a password vault mechanism
-- Example in shell: export ENV_MY_APP_PASSWORD='YourSecurePassword'

-- Grant only necessary privileges to the new user for the new database
GRANT SELECT, INSERT, UPDATE, DELETE ON my_application_db.* TO 'my_app_user'@'localhost';

-- Ensure the privileges are reloaded and applied
FLUSH PRIVILEGES;
