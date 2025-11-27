from utils.db_connection import get_db_connection, run_select_query


def main():
    # Basic connection test
    conn = get_db_connection()
    if conn is None:
        print("❌ Connection failed. Check MySQL server and .env file.")
        return

    print("✅ Connected to MySQL successfully!")
    conn.close()

    # Test a SELECT query on your sample data
    try:
        rows = run_select_query("SELECT * FROM teams;")
        print("\nTeams table:")
        for row in rows:
            print(row)
    except Exception as e:
        print("❌ Error running test query:", e)


if __name__ == "__main__":
    main()
