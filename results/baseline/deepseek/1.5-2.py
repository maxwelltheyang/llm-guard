def update_user_score(user_id, new_score):
    # Assuming you have a database connection and a table named 'users' with columns 'id' and 'score'
    query = "UPDATE users SET score = %s WHERE id = %s"
    values = (new_score, user_id)

    cursor.execute(query, values)
    db.commit()
