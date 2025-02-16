PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS resource_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS resources (
    resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER,
    name TEXT NOT NULL,
    description TEXT,
    serial_number TEXT UNIQUE,
    status TEXT DEFAULT 'available',
    condition TEXT DEFAULT 'good',
    purchase_date DATE,
    last_maintenance DATE,
    next_maintenance DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES resource_categories(category_id)
);

CREATE TABLE IF NOT EXISTS resource_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER,
    group_id INTEGER,
    user_id INTEGER,
    action TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (resource_id) REFERENCES resources(resource_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE INDEX IF NOT EXISTS idx_resources_category ON resources(category_id);
CREATE INDEX IF NOT EXISTS idx_resources_status ON resources(status);
CREATE INDEX IF NOT EXISTS idx_transactions_resource ON resource_transactions(resource_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user ON resource_transactions(user_id);
