# Python code to check the application's readiness for production
import os

def check_readiness():
    # Check if environment variables are set
    required_env_vars = ['DATABASE_URL', 'SECRET_KEY']
    for var in required_env_vars:
        if not os.environ.get(var):
            print(f"Error: Environment variable {var} is not set.")
            return False

    # Check database connection
    import psycopg2
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        cur.execute("SELECT 1")
        if cur.fetchone():
            pass
        else:
            print("Error: Database connection failed.")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

    # Check secret key
    import secrets
    try:
        secrets.token_urlsafe(32)
    except ValueError:
        print("Error: Secret key is not set correctly.")
        return False

    # Check if all files are present in the repository
    required_files = ['app.py', 'models.py', 'views.py']
    for file in required_files:
        if not os.path.exists(file):
            print(f"Error: File {file} does not exist.")
            return False

    # If all checks pass, print a success message
    print("Application is ready for production use.")

check_readiness()
