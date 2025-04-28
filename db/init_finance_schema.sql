-- ==========================================
-- Create Tables for Finance + Dunning Schema
-- SQLite-Optimized
-- ==========================================

PRAGMA foreign_keys = ON;

-- Customers Table
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    country_code TEXT
);

-- Vendors Table
CREATE TABLE vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    country_code TEXT
);

-- Invoices Table
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    invoice_date DATE,
    due_date DATE,
    total_amount REAL,
    currency TEXT,
    status TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Payments Table
CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER,
    payment_date DATE,
    amount REAL,
    payment_method_id INTEGER,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id)
);

-- Payment Methods Table
CREATE TABLE payment_methods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

-- Dunning Levels Table
CREATE TABLE dunning_levels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level INTEGER,
    description TEXT
);

-- Dunning Runs Table
CREATE TABLE dunning_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_date DATE
);

-- Dunning Entries Table
CREATE TABLE dunning_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER,
    dunning_run_id INTEGER,
    dunning_level_id INTEGER,
    dunning_date DATE,
    fees REAL,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id),
    FOREIGN KEY (dunning_run_id) REFERENCES dunning_runs(id),
    FOREIGN KEY (dunning_level_id) REFERENCES dunning_levels(id)
);

-- Accounts Table
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_number TEXT,
    description TEXT
);

-- Account Postings Table
CREATE TABLE account_postings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER,
    posting_date DATE,
    amount REAL,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);

-- Cost Centers Table
CREATE TABLE cost_centers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

-- Projects Table
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    customer_id INTEGER,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Contracts Table
CREATE TABLE contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    contract_date DATE,
    total_value REAL,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Payment Plans Table
CREATE TABLE payment_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER,
    installment_number INTEGER,
    due_date DATE,
    amount REAL,
    FOREIGN KEY (contract_id) REFERENCES contracts(id)
);

-- Users Table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    role TEXT
);

-- Audit Logs Table
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Reminders Table
CREATE TABLE reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    reminder_date DATE,
    note TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Currencies Table
CREATE TABLE currencies (
    code TEXT PRIMARY KEY,
    name TEXT
);

-- Countries Table
CREATE TABLE countries (
    code TEXT PRIMARY KEY,
    name TEXT
);

-- Address Book Table
CREATE TABLE address_book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT, -- 'customer' or 'vendor'
    entity_id INTEGER,
    street TEXT,
    city TEXT,
    postal_code TEXT,
    country_code TEXT,
    FOREIGN KEY (country_code) REFERENCES countries(code)
);

-- ==========================================
-- Example Inserts
-- ==========================================

INSERT INTO customers (name, email, phone, country_code) VALUES
("Muster GmbH", "info@muster.de", "123456789", "DE"),
("Beispiel AG", "kontakt@beispiel.at", "987654321", "AT"),
("Sample Corp", "support@sample.com", "555-5555", "US");

INSERT INTO vendors (name, email, phone, country_code) VALUES
("Lieferant1 GmbH", "sales@lieferant1.de", "123123123", "DE"),
("Supplier2 Inc", "info@supplier2.com", "321321321", "US");

INSERT INTO invoices (customer_id, invoice_date, due_date, total_amount, currency, status) VALUES
(1, "2024-01-15", "2024-02-15", 1500.00, "EUR", "open"),
(2, "2024-02-01", "2024-03-01", 2500.00, "EUR", "paid");

INSERT INTO dunning_levels (level, description) VALUES
(1, "1. Mahnung"),
(2, "2. Mahnung"),
(3, "Letzte Mahnung");

INSERT INTO countries (code, name) VALUES
("DE", "Germany"),
("AT", "Austria"),
("US", "United States");

INSERT INTO currencies (code, name) VALUES
("EUR", "Euro"),
("USD", "US Dollar");
