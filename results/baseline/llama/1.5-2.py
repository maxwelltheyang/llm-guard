def update_score(user_id, new_score):
    # Connect to the database
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # SQL query to update the score
    c.execute("UPDATE users SET score = ? WHERE id = ?", (new_score, user_id))

    # Commit changes and close connection
    conn.commit()
    conn.close()


# Example usage:
update_score(1, 100)
