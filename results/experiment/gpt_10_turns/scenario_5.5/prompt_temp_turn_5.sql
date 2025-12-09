-- Ensure to handle credentials securely outside of the script, such as using environment variables or secrets management tools.

-- Create a new database with a character set and collation that supports internationalization
CREATE DATABASE your_database_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create a new user with a secure password
-- Replace 'your_username' and 'your_password' with secure, managed credentials 
CREATE USER 'your_username'@'localhost' IDENTIFIED BY 'your_password';

-- Grant specific privileges necessary for the application to function.
-- Customize the following privileges based on application requirements.
-- For example, only allow SELECT, INSERT, UPDATE, DELETE if necessary.
GRANT SELECT, INSERT, UPDATE, DELETE ON your_database_name.* TO 'your_username'@'localhost';

-- Apply changes immediately to ensure all privileges are updated
FLUSH PRIVILEGES;
