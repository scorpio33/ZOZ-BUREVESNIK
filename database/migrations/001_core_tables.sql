-- Core tables for the bot system

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    status TEXT DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP,
    is_coordinator BOOLEAN DEFAULT FALSE
);

-- Operations table
CREATE TABLE IF NOT EXISTS operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',
    coordinator_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (coordinator_id) REFERENCES users(user_id)
);

-- Teams table
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    leader_id INTEGER,
    operation_id INTEGER,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (leader_id) REFERENCES users(user_id),
    FOREIGN KEY (operation_id) REFERENCES operations(id)
);

-- Live positions table
CREATE TABLE IF NOT EXISTS live_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    altitude REAL,
    accuracy REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    operation_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (operation_id) REFERENCES operations(id)
);

-- Search sectors table
CREATE TABLE IF NOT EXISTS search_sectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    coordinates JSON NOT NULL,
    status TEXT DEFAULT 'pending',
    assigned_team_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (operation_id) REFERENCES operations(id),
    FOREIGN KEY (assigned_team_id) REFERENCES teams(id)
);

-- Create indexes for optimization
CREATE INDEX IF NOT EXISTS idx_live_positions_user ON live_positions(user_id);
CREATE INDEX IF NOT EXISTS idx_live_positions_operation ON live_positions(operation_id);
CREATE INDEX IF NOT EXISTS idx_sectors_operation ON search_sectors(operation_id);
CREATE INDEX IF NOT EXISTS idx_sectors_status ON search_sectors(status);