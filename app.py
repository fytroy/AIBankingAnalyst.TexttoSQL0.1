import pyodbc
import pandas as pd
import pathlib
import google.generativeai as genai
import warnings
import os # <-- This is the new library

# --- 1. SET UP YOUR API KEY ---
# The script will now read the key from your computer's environment
YOUR_API_KEY = os.environ.get("GOOGLE_API_KEY")

# This check now looks for the environment variable
if YOUR_API_KEY is None:
    print("❌ Error: 'GOOGLE_API_KEY' environment variable not set.")
    print("   Please run 'setx GOOGLE_API_KEY \"YOUR_KEY_HERE\"' in your terminal.")
    print("   IMPORTANT: You must CLOSE and REOPEN your terminal after running setx.")
    exit()

# --- 2. SET UP DATABASE CONNECTION ---
SERVER_NAME = "ROYSHP"
DATABASE_NAME = "BankingDB"
conn_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    f"Trusted_Connection=yes;"
)

# Suppress pandas UserWarning for pyodbc
warnings.filterwarnings("ignore", category=UserWarning, module="pandas")

# --- 3. CONFIGURE THE AI MODEL ---
try:
    genai.configure(api_key=YOUR_API_KEY)
    model = genai.GenerativeModel('models/gemini-pro-latest')
except Exception as e:
    print(f"❌ Error configuring AI model: {e}")
    print("   Please ensure your API key is correct and you have internet access.")
    exit()

# --- 4. LOAD THE AI's "BRAIN" (The Database Schema) ---
try:
    schema = pathlib.Path("db_schema.txt").read_text()
except FileNotFoundError:
    print("❌ Error: 'db_schema.txt' not found. Please run 'read_schema.py' first.")
    exit()

# --- 5. HELPER FUNCTIONS (No changes here) ---
def get_sql_from_ai(user_question):
    """Sends schema and question to AI, gets SQL query back."""
    prompt = f"""
    You are an expert MS-SQL data analyst. Based on the database schema below,
    write a single, valid MS-SQL query to answer the user's question.
    Only return the SQL query and nothing else.

    SCHEMA:
    {schema}

    USER QUESTION:
    "{user_question}"

    SQL QUERY:
    """
    try:
        response = model.generate_content(prompt)
        # Clean up the response to get only the SQL
        sql_query = response.text.strip().replace("```sql", "").replace("```", "")
        return sql_query
    except Exception as e:
        print(f"\n❌ Error generating SQL: {e}")
        return None

def get_insight_from_ai(question, data):
    """Sends question and data to AI, gets human-readable insight back."""
    prompt = f"""
    You are a helpful bank manager. A user asked this question:
    "{question}"

    You ran a query and got this data as a result:
    "{data}"

    Based on the question and the data, write a single, friendly,
    one-sentence business insight. If the data is empty,
    say that no results were found.

    INSIGHT:
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"\n❌ Error generating insight: {e}")
        return "I was unable to analyze the results."

def run_query(sql_query):
    """Connects to the DB, runs the query, and returns a DataFrame."""
    try:
        with pyodbc.connect(conn_string) as conn:
            # Use pandas to run the query and return a neat table
            df = pd.read_sql(sql_query, conn)
            return df
    except pyodbc.Error as e:
        # This catches errors in the SQL syntax
        print(f"\n❌ SQL Error: {e}")
        print("   The AI may have generated an invalid query. Please try rephrasing your question.")
        return None
    except Exception as e:
        print(f"\n❌ Error running query: {e}")
        return None

# --- 6. MAIN APPLICATION LOOP (No changes here) ---
print("✅ AI Banking Analyst is online. Chat with your database!")
print("   Type 'exit' to quit.\n")

while True:
    try:
        # Get user question
        user_question = input("Ask a question (e.g., 'How many customers do we have?'):\n> ")

        if user_question.lower() == 'exit':
            break

        # --- AI Step 1: Generate SQL ---
        print("\n🤖 AI is thinking... (Generating SQL)")
        sql_query = get_sql_from_ai(user_question)

        if not sql_query:
            continue

        print(f"\nGenerated SQL:\n{sql_query}\n")

        # --- AI Step 2: Run Query ---
        print("Running query against BankingDB...")
        data_df = run_query(sql_query)

        if data_df is None:
            continue # Error already printed by run_query

        print(f"\nQuery Results:\n{data_df.to_string()}\n")

        # --- AI Step 3: Generate Insight ---
        print("🤖 AI is thinking... (Analyzing results)")
        insight = get_insight_from_ai(user_question, data_df.to_string())

        print(f"\n-------------------\n💡 AI BANKING INSIGHT:\n{insight}\n-------------------\n")

    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}\n")

print("\n👋 AI Banking Analyst signing off. Goodbye!")