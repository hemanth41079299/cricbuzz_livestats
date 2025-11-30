import mysql.connector
from mysql.connector import Error
import pandas as pd


# --------------------------------------------------
# 1️⃣ Create Connection
# --------------------------------------------------
def create_connection(host, user, passwd, database=None):
    """
    Create a new MySQL connection.
    NOT cached — Streamlit reruns may occur often.
    """
    return mysql.connector.connect(
        host=host,
        user=user,
        password=passwd,
        database=database,
        autocommit=True,
    )


# --------------------------------------------------
# 2️⃣ Discover Full Schema (DB → Tables → Columns)
# --------------------------------------------------
def get_mysql_schema(host, user, passwd):
    """
    Returns nested dict with DBs → tables → column metadata.
    System DBs excluded.
    """
    conn = create_connection(host, user, passwd)
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    all_databases = [db[0] for db in cursor]

    excluded = {"information_schema", "performance_schema", "mysql", "sys"}
    full_schema = {}

    for db_name in all_databases:
        if db_name in excluded:
            continue

        try:
            db_conn = create_connection(host, user, passwd, db_name)
            db_cur = db_conn.cursor()

            # Only real tables (skip views)
            db_cur.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
            tables = db_cur.fetchall()
            if not tables:
                continue

            db_info = {
                "tables": {},
                "views": {},
                "functions": {},
                "procedures": {},
            }

            # Table columns
            for table_row in tables:
                table_name = table_row[0]
                col_sql = """
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY,
                           COLUMN_DEFAULT, EXTRA
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                    ORDER BY ORDINAL_POSITION
                """
                db_cur.execute(col_sql, (db_name, table_name))
                cols = db_cur.fetchall()

                db_info["tables"][table_name] = [
                    {
                        "name": c[0],
                        "type": c[1],
                        "nullable": c[2],
                        "key": c[3],
                        "default": c[4],
                        "extra": c[5],
                    }
                    for c in cols
                ]

            # Views
            db_cur.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW'")
            for v in db_cur.fetchall():
                db_info["views"][v[0]] = {}

            db_cur.close()
            db_conn.close()

            full_schema[db_name] = db_info

        except Error:
            continue

    cursor.close()
    conn.close()
    return full_schema


# --------------------------------------------------
# 3️⃣ Helpers: DB, Tables, Columns
# --------------------------------------------------
def list_databases(host, user, passwd):
    schema = get_mysql_schema(host, user, passwd)
    return sorted(schema.keys())


def list_tables(host, user, passwd, database):
    schema = get_mysql_schema(host, user, passwd)
    db = schema.get(database, {})
    return sorted(db.get("tables", {}).keys())


def get_table_columns(host, user, passwd, database, table):
    schema = get_mysql_schema(host, user, passwd)
    return schema.get(database, {}).get("tables", {}).get(table, [])


# --------------------------------------------------
# 4️⃣ Fetch table (SELECT * LIMIT)
# --------------------------------------------------
def fetch_table(host, user, passwd, database, table, limit=200):
    """
    Return DataFrame and exact SQL used.
    """
    conn = create_connection(host, user, passwd, database)
    sql = f"SELECT * FROM `{table}` LIMIT {int(limit)};"
    df = pd.read_sql(sql, conn)
    conn.close()
    return df, sql


# --------------------------------------------------
# 5️⃣ Run SELECT safely
# --------------------------------------------------
def run_select(host, user, passwd, database, select_sql):
    """
    Run SELECT-only query.
    Raises error if query doesn't start with SELECT.
    """
    if not select_sql.strip().lower().startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")

    conn = create_connection(host, user, passwd, database)
    df = pd.read_sql(select_sql, conn)
    conn.close()
    return df


# --------------------------------------------------
# 6️⃣ Insert one row (safe param binding)
# --------------------------------------------------
def insert_row(host, user, passwd, database, table, data):
    """
    Insert a single row.
    Returns (affected_rows, SQL preview).
    """

    cols = [f"`{c}`" for c in data.keys()]
    placeholders = ", ".join(["%s"] * len(cols))

    sql = f"INSERT INTO `{table}` ({', '.join(cols)}) VALUES ({placeholders});"
    values = list(data.values())

    conn = create_connection(host, user, passwd, database)
    cur = conn.cursor()
    cur.execute(sql, values)
    affected = cur.rowcount
    cur.close()
    conn.close()

    return affected, sql


# --------------------------------------------------
# 7️⃣ Delete rows (forced WHERE)
# --------------------------------------------------
def delete_rows(host, user, passwd, database, table, where_clause):
    where = where_clause.strip()
    if not where:
        raise ValueError("Refusing to DELETE without WHERE clause.")

    sql = f"DELETE FROM `{table}` WHERE {where};"

    conn = create_connection(host, user, passwd, database)
    cur = conn.cursor()
    cur.execute(sql)
    affected = cur.rowcount
    cur.close()
    conn.close()

    return affected, sql


# --------------------------------------------------
# 8️⃣ Update rows (forced SET + WHERE)
# --------------------------------------------------
def execute_update(host, user, passwd, database, table, set_clause, where_clause):
    set_part = set_clause.strip()
    where_part = where_clause.strip()

    if not set_part:
        raise ValueError("SET clause cannot be empty.")
    if not where_part:
        raise ValueError("Refusing to UPDATE without WHERE clause.")

    sql = f"UPDATE `{table}` SET {set_part} WHERE {where_part};"

    conn = create_connection(host, user, passwd, database)
    cur = conn.cursor()
    cur.execute(sql)
    affected = cur.rowcount
    cur.close()
    conn.close()

    return affected, sql
