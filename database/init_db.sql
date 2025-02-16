-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    full_name TEXT,
    password_hash TEXT,
    salt TEXT,
    role TEXT DEFAULT 'user',
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Password recovery table
CREATE TABLE IF NOT EXISTS password_recovery (
    user_id INTEGER PRIMARY KEY,
    recovery_code TEXT,
    expires_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Coordinator requests table
CREATE TABLE IF NOT EXISTS coordinator_requests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    full_name TEXT,
    region TEXT,
    phone TEXT,
    team_name TEXT,
    position TEXT,
    experience INTEGER,
    work_time TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);