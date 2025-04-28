import sqlite3
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker
faker = Faker()

# Connect to the database
conn = sqlite3.connect('finance_test.db')
cursor = conn.cursor()

# Helper function
def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

# Seed countries
countries = [('DE', 'Germany'), ('AT', 'Austria'), ('US', 'United States'), ('GB', 'United Kingdom'), ('FR', 'France'), ('IT', 'Italy'), ('ES', 'Spain'), ('CH', 'Switzerland'), ('NL', 'Netherlands'), ('BE', 'Belgium')]
cursor.executemany("INSERT OR IGNORE INTO countries (code, name) VALUES (?, ?)", countries)

# Seed currencies
currencies = [('EUR', 'Euro'), ('USD', 'US Dollar'), ('GBP', 'British Pound')]
cursor.executemany("INSERT OR IGNORE INTO currencies (code, name) VALUES (?, ?)", currencies)

# Seed payment methods
payment_methods = [('Bank Transfer',), ('Credit Card',), ('PayPal',), ('Cash',), ('Direct Debit',)]
cursor.executemany("INSERT OR IGNORE INTO payment_methods (name) VALUES (?)", payment_methods)

# Seed customers
for _ in range(100):
    cursor.execute("INSERT INTO customers (name, email, phone, country_code) VALUES (?, ?, ?, ?)", (faker.company(), faker.company_email(), faker.phone_number(), random.choice(countries)[0]))

# Seed vendors
for _ in range(50):
    cursor.execute("INSERT INTO vendors (name, email, phone, country_code) VALUES (?, ?, ?, ?)", (faker.company(), faker.company_email(), faker.phone_number(), random.choice(countries)[0]))

# Seed accounts
for _ in range(20):
    cursor.execute("INSERT INTO accounts (account_number, description) VALUES (?, ?)", (faker.bban(), faker.word()))

# Seed cost centers
for _ in range(10):
    cursor.execute("INSERT INTO cost_centers (name) VALUES (?)", (faker.bs(),))

# Seed users
for _ in range(20):
    cursor.execute("INSERT INTO users (username, role) VALUES (?, ?)", (faker.user_name(), random.choice(['admin', 'accountant', 'auditor'])))

# Seed projects
customer_ids = [row[0] for row in cursor.execute("SELECT id FROM customers").fetchall()]
for _ in range(20):
    cursor.execute("INSERT INTO projects (name, customer_id) VALUES (?, ?)", (faker.catch_phrase(), random.choice(customer_ids)))

# Seed contracts
for _ in range(50):
    cursor.execute("INSERT INTO contracts (customer_id, contract_date, total_value) VALUES (?, ?, ?)", (random.choice(customer_ids), random_date(datetime(2022, 1, 1), datetime(2024, 6, 1)).date(), round(random.uniform(10000, 50000), 2)))

# Seed invoices
for _ in range(500):
    customer_id = random.choice(customer_ids)
    invoice_date = random_date(datetime(2023, 1, 1), datetime(2024, 6, 1))
    due_date = invoice_date + timedelta(days=random.choice([30, 45, 60]))
    total_amount = round(random.uniform(100, 10000), 2)
    status = random.choice(['open', 'paid', 'overdue'])
    cursor.execute("INSERT INTO invoices (customer_id, invoice_date, due_date, total_amount, currency, status) VALUES (?, ?, ?, ?, ?, ?)", (customer_id, invoice_date.date(), due_date.date(), total_amount, random.choice(['EUR', 'USD', 'GBP']), status))

# Seed payments
invoice_ids = [row[0] for row in cursor.execute("SELECT id FROM invoices").fetchall()]
payment_method_ids = [row[0] for row in cursor.execute("SELECT id FROM payment_methods").fetchall()]
for _ in range(300):
    cursor.execute("INSERT INTO payments (invoice_id, payment_date, amount, payment_method_id) VALUES (?, ?, ?, ?)", (random.choice(invoice_ids), random_date(datetime(2023, 1, 1), datetime(2024, 6, 1)).date(), round(random.uniform(50, 10000), 2), random.choice(payment_method_ids)))

# Seed dunning levels
cursor.execute("INSERT OR IGNORE INTO dunning_levels (level, description) VALUES (1, '1st Reminder'), (2, '2nd Reminder'), (3, 'Final Reminder')")

# Seed dunning runs
for _ in range(5):
    cursor.execute("INSERT INTO dunning_runs (run_date) VALUES (?)", (random_date(datetime(2023, 1, 1), datetime(2024, 6, 1)).date(),))

# Seed dunning entries
dunning_run_ids = [row[0] for row in cursor.execute("SELECT id FROM dunning_runs").fetchall()]
dunning_level_ids = [row[0] for row in cursor.execute("SELECT id FROM dunning_levels").fetchall()]
for _ in range(200):
    cursor.execute("INSERT INTO dunning_entries (invoice_id, dunning_run_id, dunning_level_id, dunning_date, fees) VALUES (?, ?, ?, ?, ?)", (random.choice(invoice_ids), random.choice(dunning_run_ids), random.choice(dunning_level_ids), random_date(datetime(2023, 2, 1), datetime(2024, 6, 1)).date(), round(random.uniform(5, 50), 2)))

# Seed payment plans
contract_ids = [row[0] for row in cursor.execute("SELECT id FROM contracts").fetchall()]
for _ in range(150):
    cursor.execute("INSERT INTO payment_plans (contract_id, installment_number, due_date, amount) VALUES (?, ?, ?, ?)", (random.choice(contract_ids), random.randint(1, 12), random_date(datetime(2024, 1, 1), datetime(2025, 12, 31)).date(), round(random.uniform(500, 5000), 2)))

# Seed account postings
account_ids = [row[0] for row in cursor.execute("SELECT id FROM accounts").fetchall()]
for _ in range(1000):
    cursor.execute("INSERT INTO account_postings (account_id, posting_date, amount) VALUES (?, ?, ?)", (random.choice(account_ids), random_date(datetime(2023, 1, 1), datetime(2024, 6, 1)).date(), round(random.uniform(-10000, 10000), 2)))

# Seed reminders
for _ in range(100):
    cursor.execute("INSERT INTO reminders (customer_id, reminder_date, note) VALUES (?, ?, ?)", (random.choice(customer_ids), random_date(datetime(2023, 1, 1), datetime(2024, 6, 1)).date(), faker.sentence()))

# Seed address book entries
for _ in range(200):
    entity_type = random.choice(['customer', 'vendor'])
    entity_id = random.choice(customer_ids if entity_type == 'customer' else [row[0] for row in cursor.execute("SELECT id FROM vendors").fetchall()])
    cursor.execute("INSERT INTO address_book (entity_type, entity_id, street, city, postal_code, country_code) VALUES (?, ?, ?, ?, ?, ?)", (entity_type, entity_id, faker.street_address(), faker.city(), faker.postcode(), random.choice(countries)[0]))

# Seed audit logs
user_ids = [row[0] for row in cursor.execute("SELECT id FROM users").fetchall()]
for _ in range(500):
    cursor.execute("INSERT INTO audit_logs (user_id, action, timestamp) VALUES (?, ?, ?)", (random.choice(user_ids), random.choice(['create_invoice', 'update_customer', 'delete_payment', 'run_dunning']), random_date(datetime(2023, 1, 1), datetime(2024, 6, 1))))

# Commit and close
conn.commit()
conn.close()

print("Alle Testdaten erfolgreich eingefügt!")
