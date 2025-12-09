-- Ensure to handle credentials securely outside of the script, such as using environment variables or secrets management tools.

-- Create a new database with a character set and collation for internationalization support
CREATE DATABASE your_database_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create a new user with a secure and managed password
-- Replace 'your_username', 'application_server_ip', and 'your_password'
-- with your specific details and a securely managed password
CREATE USER 'your_username'@'application_server_ip' IDENTIFIED BY 'your_password';

-- Grant specific and necessary privileges for application functionality
-- Adjust the following privileges based on the application's requirements
GRANT SELECT, INSERT, UPDATE, DELETE ON your_database_name.* TO 'your_username'@'application_server_ip';

-- Apply privilege changes immediately
FLUSH PRIVILEGES;
