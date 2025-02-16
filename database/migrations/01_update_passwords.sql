
-- Обновление структуры таблицы пользователей для новой системы паролей
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    password_hash TEXT,
    salt TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    status TEXT DEFAULT 'user',
    coordinator_level INTEGER DEFAULT 0,
    experience INTEGER DEFAULT 0
);

-- Таблица для восстановления паролей
CREATE TABLE IF NOT EXISTS password_recovery (
    user_id INTEGER PRIMARY KEY,
    recovery_code TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    attempts INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);
CREATE INDEX IF NOT EXISTS idx_users_coordinator ON users(coordinator_level);
