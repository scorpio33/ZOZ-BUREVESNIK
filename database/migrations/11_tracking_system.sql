-- Таблица для хранения треков
CREATE TABLE IF NOT EXISTS user_tracks (
    track_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    group_id INTEGER,
    coordinates TEXT NOT NULL,  -- JSON array of coordinates
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    distance FLOAT DEFAULT 0,
    status TEXT DEFAULT 'active',
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (group_id) REFERENCES search_groups(group_id)
);

-- Таблица для хранения текущих позиций
CREATE TABLE IF NOT EXISTS live_positions (
    position_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    group_id INTEGER,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    accuracy FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (group_id) REFERENCES search_groups(group_id)
);

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_tracks_user ON user_tracks(user_id);
CREATE INDEX IF NOT EXISTS idx_tracks_group ON user_tracks(group_id);
CREATE INDEX IF NOT EXISTS idx_positions_user ON live_positions(user_id);
CREATE INDEX IF NOT EXISTS idx_positions_group ON live_positions(group_id);
CREATE INDEX IF NOT EXISTS idx_positions_time ON live_positions(timestamp);