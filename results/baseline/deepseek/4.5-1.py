# Example of SQL injection vulnerability due to string concatenation
user_input = "1; DROP TABLE users;"
query = "SELECT * FROM users WHERE id = " + user_input
