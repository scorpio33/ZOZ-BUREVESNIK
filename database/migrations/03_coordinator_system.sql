

-- Таблица для заявок на статус координатора
CREATE TABLE IF NOT EXISTS coordinator_requests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    full_name TEXT NOT NULL,
    region TEXT NOT NULL,
    phone TEXT NOT NULL,
    team_name TEXT NOT NULL,
    position TEXT NOT NULL,
    search_count INTEGER NOT NULL,
    experience_time TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    processed_by INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (processed_by) REFERENCES users(user_id)
);

-- Индексы
CREATE INDEX IF NOT EXISTS idx_requests_status ON coordinator_requests(status);
CREATE INDEX IF NOT EXISTS idx_requests_user ON coordinator_requests(user_id);
