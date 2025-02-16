-- Создание таблиц для секторов и отслеживания

-- Таблица для хранения live-позиций
CREATE TABLE IF NOT EXISTS live_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    altitude REAL,
    accuracy REAL,
    sector_id INTEGER,
    operation_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (sector_id) REFERENCES search_sectors(id),
    FOREIGN KEY (operation_id) REFERENCES operations(id)
);

-- Таблица для поисковых секторов
CREATE TABLE IF NOT EXISTS search_sectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    coordinates JSON NOT NULL,
    status TEXT DEFAULT 'pending',
    coordinator_id INTEGER,
    assigned_team_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (operation_id) REFERENCES operations(id),
    FOREIGN KEY (coordinator_id) REFERENCES users(user_id),
    FOREIGN KEY (assigned_team_id) REFERENCES teams(id)
);

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_live_positions_user ON live_positions(user_id);
CREATE INDEX IF NOT EXISTS idx_live_positions_operation ON live_positions(operation_id);
CREATE INDEX IF NOT EXISTS idx_live_positions_sector ON live_positions(sector_id);
CREATE INDEX IF NOT EXISTS idx_sectors_operation ON search_sectors(operation_id);
CREATE INDEX IF NOT EXISTS idx_sectors_status ON search_sectors(status);

-- Триггер для автоматического обновления completed_at
CREATE TRIGGER IF NOT EXISTS update_sector_completed_at
AFTER UPDATE OF status ON search_sectors
WHEN NEW.status = 'completed' AND OLD.status != 'completed'
BEGIN
    UPDATE search_sectors 
    SET completed_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;