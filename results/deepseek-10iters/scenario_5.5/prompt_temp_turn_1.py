cursor.execute(f"CREATE USER '{user}'@'localhost' IDENTIFIED WITH mysql_native_password BY '{password}'")
