-- Таблица для заявок на статус координатора
CREATE TABLE IF NOT EXISTS coordinator_requests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    username TEXT,
    full_name TEXT,
    region TEXT,
    phone_number TEXT,
    team_name TEXT,
    position TEXT,
    search_count INTEGER,
    experience_years INTEGER,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Добавление поля is_coordinator в таблицу users
ALTER TABLE users ADD COLUMN is_coordinator BOOLEAN DEFAULT FALSE;