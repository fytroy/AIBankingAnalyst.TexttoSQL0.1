 AI Banking Analyst (Text-to-SQL)

Lightweight CLI helper that turns natural language banking questions into MS SQL Server queries using Google Gemini, runs them against your `BankingDB`, and returns a short business insight.

 Project Flow
- Discover schema: run `read_schema.py` to export your database structure into `db_schema.txt` for the model prompt.
- Seed sample data (optional): run `generate_data.py` to populate dimension and fact tables with realistic fake data.
- Chat with the database: run `app.py`; it builds SQL with Gemini, executes it via `pyodbc`, and summarizes results.
- Inspect available models: run `check_models.py` to list Google AI models that support `generateContent`.

 Prerequisites
- Python 3.9+ (tested with recent 3.x)
- SQL Server with a database named `BankingDB` accessible on your machine
- ODBC Driver 17 for SQL Server installed
- Google AI Studio API key with access to Gemini models
- Windows: ensure `setx` is available in your shell (default on recent versions)

 Setup
1. Create and activate a virtual environment (recommended).
2. Install dependencies:
   ```bash
   pip install google-generativeai pandas pyodbc faker
   ```
3. Set your API key (reopen the terminal after running this):
   ```bash
   setx GOOGLE_API_KEY "YOUR_KEY_HERE"
   ```
4. Confirm SQL Server connectivity: the scripts assume server `ROYSHP`, database `BankingDB`, trusted auth. Update `SERVER_NAME` or `DATABASE_NAME` in the scripts if yours differ.

 Database Preparation
1. Create tables: run the SQL in `CREATE ALL TABLES.sql` against `BankingDB`.
2. Export schema for the model:
   ```bash
   python read_schema.py
   ```
   This writes `db_schema.txt`, which `app.py` requires at startup.
3. (Optional) Load demo data:
   ```bash
   python generate_data.py
   ```
   Inserts transaction types, customers, accounts, and ~20k transactions, then commits.

 Running the Analyst
```bash
python app.py
```
- Type banking questions (e.g., "total deposits last month?").
- The tool prints the generated SQL, query results, and a one-sentence insight.
- Type `exit` to quit.

 Model Discovery (optional)
List available Gemini models that support `generateContent`:
```bash
python check_models.py
```

 Troubleshooting
- Missing API key: ensure `GOOGLE_API_KEY` is set, then reopen the terminal.
- Schema file missing: run `read_schema.py` to regenerate `db_schema.txt` before `app.py`.
- SQL errors: rephrase the question; the AI may produce invalid SQL. You can also inspect and fix the SQL before rerunning.
- Connection issues: verify `SERVER_NAME`, `DATABASE_NAME`, and that ODBC Driver 17 is installed.

 Notes
- The scripts use trusted authentication; adjust connection strings if you require SQL auth.
- `generate_data.py` uses Faker; reruns will insert additional rows. Truncate tables first if you need a clean slate.
