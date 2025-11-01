import pyodbc
import pandas as pd
from faker import Faker
import random
import datetime

# --- 1. SET YOUR DATABASE DETAILS ---
SERVER_NAME = "ROYSHP"
DATABASE_NAME = "BankingDB"  # <-- Your new database

# --- 2. CONNECT TO THE DATABASE ---
conn_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    f"Trusted_Connection=yes;"
    f"autocommit=False" # We will commit at the end
)

connection = None
cursor = None
fake = Faker()

try:
    print(f"Connecting to SQL Server '{SERVER_NAME}'...")
    connection = pyodbc.connect(conn_string)
    cursor = connection.cursor()
    print(f"✅ Success! Connected to '{DATABASE_NAME}'.")

    # --- STEP 1: POPULATE Dim_TransactionTypes ---
    print("\nPopulating 'Dim_TransactionTypes'...")
    transaction_types = [
        ('Deposit', 0), ('Withdrawal', 1), ('Transfer Out', 1), ('Transfer In', 0),
        ('Online Purchase', 1), ('ATM Withdrawal', 1), ('Salary', 0), ('Bill Payment', 1)
    ]
    cursor.executemany(
        "INSERT INTO Dim_TransactionTypes (TransactionTypeName, IsDebit) VALUES (?, ?)",
        transaction_types
    )
    print(f"✅ Added {len(transaction_types)} transaction types.")

    # Fetch the new TransactionTypeKeys for later
    cursor.execute("SELECT TransactionTypeKey, IsDebit FROM Dim_TransactionTypes")
    ttype_keys = cursor.fetchall()

    # --- STEP 2: GENERATE AND INSERT 500 CUSTOMERS ---
    print("\nGenerating 500 new customers for 'Dim_Customers'...")
    customers_to_insert = []
    for i in range(500):
        cust_id = f"CUST{1000 + i}"
        reg_date = fake.date_between(start_date='-5y', end_date='today')
        customers_to_insert.append((
            cust_id, fake.first_name(), fake.last_name(), fake.email(),
            fake.city(), fake.country(), reg_date
        ))

    cursor.executemany(
        "INSERT INTO Dim_Customers (CustomerID, FirstName, LastName, Email, City, Country, RegistrationDate) VALUES (?, ?, ?, ?, ?, ?, ?)",
        customers_to_insert
    )
    print(f"✅ Added {len(customers_to_insert)} customers.")

    # Fetch the new CustomerKeys for later
    cursor.execute("SELECT CustomerKey FROM Dim_Customers")
    customer_keys = [row[0] for row in cursor.fetchall()]

    # --- STEP 3: GENERATE AND INSERT ~750 ACCOUNTS ---
    print("\nGenerating ~750 new accounts for 'Dim_Accounts'...")
    accounts_to_insert = []
    account_id_counter = 20000
    for cust_key in customer_keys:
        # Give each customer 1 or 2 accounts
        for _ in range(random.choice([1, 2])):
            acc_id = f"ACC{account_id_counter}"
            open_date = fake.date_between(start_date='-3y', end_date='today')
            accounts_to_insert.append((
                acc_id, cust_key, random.choice(['Checking', 'Savings']), open_date, 'Active'
            ))
            account_id_counter += 1

    cursor.executemany(
        "INSERT INTO Dim_Accounts (AccountID, CustomerKey, AccountType, OpenDate, Status) VALUES (?, ?, ?, ?, ?)",
        accounts_to_insert
    )
    print(f"✅ Added {len(accounts_to_insert)} accounts.")

    # Fetch the new AccountKeys for later
    cursor.execute("SELECT AccountKey FROM Dim_Accounts")
    account_keys = [row[0] for row in cursor.fetchall()]

    # --- STEP 4: GENERATE AND INSERT 20,000 TRANSACTIONS ---
    print("\nGenerating 20,000 transactions for 'Fact_Transactions'...")
    print("This may take a minute...")

    # Fetch valid DateKeys from 2023-2025
    cursor.execute("SELECT DateKey FROM Dim_Date")
    date_keys = [row[0] for row in cursor.fetchall()]

    transactions_to_insert = []
    for _ in range(20000):
        ttype_key, is_debit = random.choice(ttype_keys)

        # Determine amount
        if ttype_key == 7: # Salary
            amount = round(random.uniform(1500, 5000), 2)
        else:
            amount = round(random.uniform(5.50, 1000.00), 2)

        # Make amount negative if it's a debit (easier for BI)
        if is_debit:
            amount = -amount

        transactions_to_insert.append((
            random.choice(date_keys),
            random.choice(account_keys),
            ttype_key,
            amount,
            fake.city() # Location
        ))

    # Use executemany for high-speed insert
    cursor.executemany(
        "INSERT INTO Fact_Transactions (DateKey, AccountKey, TransactionTypeKey, Amount, Location) VALUES (?, ?, ?, ?, ?)",
        transactions_to_insert
    )
    print(f"✅ Added {len(transactions_to_insert)} transactions.")

    # --- FINAL STEP: COMMIT ALL CHANGES ---
    print("\nCommitting all changes to the database...")
    connection.commit()
    print("✅✅✅ Database populated successfully!")

except Exception as e:
    print(f"❌ An unexpected error occurred: {e}")
    print("Rolling back changes...")
    if 'connection' in locals() and connection:
        connection.rollback()
finally:
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'connection' in locals() and connection:
        connection.close()
        print("\nSQL Server connection is closed.")