import sqlite3

def connect_to_database(db_name):
    conn = sqlite3.connect(db_name)
    return conn.cursor()

def create_table(conn, table_name):
    cursor = conn.cursor()
    query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL
        );
    """
    cursor.execute(query)

def insert_user(conn, table_name, username):
    query = f"""
        INSERT INTO {table_name} (username)
        VALUES (?);
    """
    conn.execute(query, (username,))

def main():
    db_name = "users.db"
    table_name = "users"

    # Connect to database
    cursor = connect_to_database(db_name)

    # Create table if not exists
    create_table(cursor, table_name)

    # Insert user into table
    username = input("Enter a username: ")
    insert_user(cursor, table_name, username)

    # Commit changes
    cursor.connection.commit()

if __name__ == "__main__":
    main()
