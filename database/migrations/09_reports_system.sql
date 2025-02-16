-- Create reports tables if they don't exist
CREATE TABLE IF NOT EXISTS operation_reports (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NOT NULL,
    report_data TEXT NOT NULL,
    FOREIGN KEY (operation_id) REFERENCES search_operations(operation_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

-- Create archived operations table
CREATE TABLE IF NOT EXISTS archived_operations (
    archive_id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id INTEGER NOT NULL,
    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    archived_by INTEGER NOT NULL,
    archive_path TEXT NOT NULL,
    metadata TEXT,
    FOREIGN KEY (operation_id) REFERENCES search_operations(operation_id),
    FOREIGN KEY (archived_by) REFERENCES users(user_id)
);

-- Create report permissions table
CREATE TABLE IF NOT EXISTS report_permissions (
    permission_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    permission_type VARCHAR(50) NOT NULL,
    granted_by INTEGER NOT NULL,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (granted_by) REFERENCES users(user_id)
);

-- Create necessary indexes
CREATE INDEX IF NOT EXISTS idx_operation_reports_operation ON operation_reports(operation_id);
CREATE INDEX IF NOT EXISTS idx_archived_operations_operation ON archived_operations(operation_id);
CREATE INDEX IF NOT EXISTS idx_report_permissions_user ON report_permissions(user_id);
