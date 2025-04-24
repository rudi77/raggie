"""Tests for the test database creation and basic queries."""
import os
import sqlite3
from pathlib import Path
from create_test_db import create_test_db, DB_PATH

def test_database_creation():
    """Test that the database is created correctly."""
    # Create the database
    create_test_db()
    
    # Verify the database exists
    assert DB_PATH.exists(), "Database file was not created"
    
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Test table structure
    cursor.execute("PRAGMA table_info(transactions)")
    columns = cursor.fetchall()
    assert len(columns) == 8, "Wrong number of columns"
    
    # Test data insertion
    cursor.execute("SELECT COUNT(*) FROM transactions")
    count = cursor.fetchone()[0]
    assert count > 0, "No records were inserted"
    
    # Test indexes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indexes = cursor.fetchall()
    assert len(indexes) >= 3, "Not all indexes were created"
    
    # Test a basic query
    cursor.execute("""
    SELECT account_name, period, amount 
    FROM transactions 
    WHERE revenue_relevant = 'Ja' 
    ORDER BY period DESC 
    LIMIT 5
    """)
    results = cursor.fetchall()
    assert len(results) > 0, "No results found for revenue_relevant = 'Ja'"
    
    # Close connection
    conn.close()

def test_data_integrity():
    """Test that the data was imported correctly."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Test specific values
    cursor.execute("""
    SELECT account_name, amount 
    FROM transactions 
    WHERE account_name = 'Musterdebitor Gewo GmbH' 
    AND period = '202401'
    """)
    results = cursor.fetchall()
    assert len(results) > 0, "No data found for Musterdebitor Gewo GmbH in 202401"
    
    # Test data types
    cursor.execute("""
    SELECT amount, credit_limit 
    FROM transactions 
    LIMIT 1
    """)
    row = cursor.fetchone()
    assert isinstance(row[0], float), "Amount is not a float"
    assert isinstance(row[1], float), "Credit limit is not a float"
    
    conn.close()

if __name__ == "__main__":
    test_database_creation()
    test_data_integrity()
    print("All tests passed!") 