"""Create a test database with sample data."""
import os
import sqlite3
import csv
from pathlib import Path
from typing import Optional

def parse_german_number(value: str) -> Optional[float]:
    """Parse a number in German format (e.g., '1.234,56' -> 1234.56)."""
    try:
        # Remove any whitespace and quotes
        value = value.strip().strip('"')
        # Replace dots with nothing (thousand separators)
        value = value.replace(".", "")
        # Replace comma with dot (decimal separator)
        value = value.replace(",", ".")
        return float(value)
    except (ValueError, AttributeError):
        return None

def create_test_db(db_path: str) -> None:
    """Create a test database with sample data.
    
    Args:
        db_path: Path to the SQLite database file
    """
    # Remove existing database if it exists
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except PermissionError:
        print(f"Warning: Could not remove existing database at {db_path}. It may be in use.")
        # Try to close any open connections
        try:
            conn = sqlite3.connect(db_path)
            conn.close()
        except:
            pass
        try:
            os.remove(db_path)
        except:
            print(f"Warning: Still could not remove database at {db_path}")
            return
    
    # Create database and tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create transactions table
    cursor.execute("""
    CREATE TABLE transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        period TEXT NOT NULL,
        customer TEXT NOT NULL,
        amount REAL NOT NULL,
        credit_limit REAL,
        revenue_relevant TEXT,
        transaction_type TEXT,
        description TEXT
    )
    """)
    
    # Read test data from CSV
    csv_path = Path(__file__).parent.parent.parent / "documents" / "text2sql_testdata.csv"
    
    try:
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Map German column names to English
                    amount = parse_german_number(row["Rechenbetrag"])
                    credit_limit = parse_german_number(row.get("Personenkonto Kreditlimit", ""))
                    
                    if amount is None:
                        print(f"Warning: Skipping row due to error: Could not parse number: {row['Rechenbetrag']}")
                        continue
                    
                    cursor.execute(
                        """
                        INSERT INTO transactions (
                            period, customer, amount, credit_limit,
                            revenue_relevant, transaction_type, description
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            row["Periode"],
                            row["Personenkonto Bezeichnung"],
                            amount,
                            credit_limit,
                            row.get("Umsatzrelevant", ""),
                            row.get("Datenart", ""),
                            row.get("Personenkonto Art", "")
                        )
                    )
                except sqlite3.Error as e:
                    print(f"Warning: Error inserting row: {e}")
                    continue
    except UnicodeDecodeError:
        # Try with a different encoding if UTF-8 fails
        with open(csv_path, "r", encoding="latin1") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Map German column names to English
                    amount = parse_german_number(row["Rechenbetrag"])
                    credit_limit = parse_german_number(row.get("Personenkonto Kreditlimit", ""))
                    
                    if amount is None:
                        print(f"Warning: Skipping row due to error: Could not parse number: {row['Rechenbetrag']}")
                        continue
                    
                    cursor.execute(
                        """
                        INSERT INTO transactions (
                            period, customer, amount, credit_limit,
                            revenue_relevant, transaction_type, description
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            row["Periode"],
                            row["Personenkonto Bezeichnung"],
                            amount,
                            credit_limit,
                            row.get("Umsatzrelevant", ""),
                            row.get("Datenart", ""),
                            row.get("Personenkonto Art", "")
                        )
                    )
                except sqlite3.Error as e:
                    print(f"Warning: Error inserting row: {e}")
                    continue
    
    # Create indexes
    cursor.execute("CREATE INDEX idx_period ON transactions(period)")
    cursor.execute("CREATE INDEX idx_customer ON transactions(customer)")
    cursor.execute("CREATE INDEX idx_revenue_relevant ON transactions(revenue_relevant)")
    
    # Commit and close
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_test_db() 