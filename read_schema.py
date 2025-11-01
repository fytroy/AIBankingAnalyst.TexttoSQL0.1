import pyodbc
import pandas as pd

# --- 1. SET YOUR DATABASE DETAILS ---
SERVER_NAME = "ROYSHP"
DATABASE_NAME = "BankingDB" # <-- Your new database

# --- 2. CONNECT TO THE DATABASE ---
conn_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    f"Trusted_Connection=yes;"
)

connection = None
try:
    print(f"Connecting to SQL Server '{SERVER_NAME}'...")
    connection = pyodbc.connect(conn_string)
    print(f"✅ Success! Connected to '{DATABASE_NAME}'.")

    # --- 3. DISCOVER THE DATABASE SCHEMA ---
    print("\nReading database schema...")

    # This query asks the database to describe itself
    sql_query = """
                SELECT
                    t.TABLE_NAME,
                    c.COLUMN_NAME,
                    c.DATA_TYPE
                FROM
                    INFORMATION_SCHEMA.TABLES AS t
                        JOIN
                    INFORMATION_SCHEMA.COLUMNS AS c ON t.TABLE_NAME = c.TABLE_NAME
                WHERE
                    t.TABLE_SCHEMA = 'dbo'  -- Standard schema
                  AND t.TABLE_TYPE = 'BASE TABLE' -- Only get real tables
                ORDER BY
                    t.TABLE_NAME, c.ORDINAL_POSITION \
                """

    df = pd.read_sql(sql_query, connection)

    # --- 4. FORMAT THE SCHEMA FOR THE AI ---
    print("Formatting schema for the AI's 'brain'...")

    schema_map = {}
    for index, row in df.iterrows():
        table = row['TABLE_NAME']
        column = f"{row['COLUMN_NAME']} ({row['DATA_TYPE']})"

        if table not in schema_map:
            schema_map[table] = []
        schema_map[table].append(column)

    # --- 5. PRINT THE AI's "KNOWLEDGE BASE" ---
    print("\n--- AI KNOWLEDGE BASE (Database Schema) ---")

    schema_string = ""
    for table, columns in schema_map.items():
        print(f"\nTable: {table}")
        schema_string += f"Table: {table}\n"
        for col in columns:
            print(f"  - {col}")
            schema_string += f"  - {col}\n"

    # We will save this string to use in the next step
    with open("db_schema.txt", "w") as f:
        f.write(schema_string)

    print("\n-------------------------------------------")
    print("\n✅ Schema saved to 'db_schema.txt'")
    print("This file is now the AI's 'knowledge' of your database.")

except pyodbc.Error as ex:
    print(f"❌ Error: {ex}")
except Exception as e:
    print(f"❌ An unexpected error occurred: {e}")
finally:
    if 'connection' in locals() and connection:
        connection.close()
        print("\nSQL Server connection is closed.")