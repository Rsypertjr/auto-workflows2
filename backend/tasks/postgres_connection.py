import psycopg2

try:
    # 1. Establish the connection to the database
    connection = psycopg2.connect(
        host='postgres-db',       # Server address (e.g., "127.0.0.1" or remote IP)
        database='postgres',     # Name of your specific database
        user='postgres',        # Your PostgreSQL username
        password='SecureProdPassword2026!',# Your PostgreSQL password
        port='5432'             # Default PostgreSQL port
    )

    # 2. Create a cursor object to execute SQL commands
    cursor = connection.cursor()
    
    # 3. Execute a query
    cursor.execute("SELECT version();")
    
    # 4. Fetch the results
    db_version = cursor.fetchone()
    print(f"Connected to PostgreSQL! Server version: {db_version}")

except Exception as error:
    print(f"Error connecting to database: {error}")

finally:
    # 5. Always close the cursor and connection to free up memory
    if 'cursor' in locals() and cursor is not None:
        cursor.close()
    if 'connection' in locals() and connection is not None:
        connection.close()
    print("Database connection closed.")
