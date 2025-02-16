-- Таблица для хранения live-позиций
CREATE TABLE IF NOT EXISTS live_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    altitude REAL,
    accuracy REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    operation_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (operation_id) REFERENCES operations(id)
);

-- Таблица для поисковых секторов
CREATE TABLE IF NOT EXISTS search_sectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    coordinates JSON NOT NULL, -- Полигон сектора
    status TEXT DEFAULT 'pending', -- pending, in_progress, completed
    assigned_team_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (operation_id) REFERENCES operations(id),
    FOREIGN KEY (assigned_team_id) REFERENCES teams(id)
);

-- Удаляем существующий индекс, если он есть
DROP INDEX IF EXISTS idx_live_positions_user;

-- Создаем индекс
CREATE INDEX idx_live_positions_user ON live_positions(user_id);

-- Проверяем существование столбцов перед их добавлением
BEGIN TRANSACTION;

-- Добавляем столбец total_distance, если его нет
SELECT CASE 
    WHEN COUNT(*) = 0 THEN
        'ALTER TABLE users ADD COLUMN total_distance FLOAT DEFAULT 0'
    ELSE
        'SELECT 1'
    END AS sql_statement
FROM pragma_table_info('users')
WHERE name = 'total_distance';

-- Добавляем столбец total_searches, если его нет
SELECT CASE 
    WHEN COUNT(*) = 0 THEN
        'ALTER TABLE users ADD COLUMN total_searches INTEGER DEFAULT 0'
    ELSE
        'SELECT 1'
    END AS sql_statement
FROM pragma_table_info('users')
WHERE name = 'total_searches';

-- Добавляем столбец total_time, если его нет
SELECT CASE 
    WHEN COUNT(*) = 0 THEN
        'ALTER TABLE users ADD COLUMN total_time INTEGER DEFAULT 0'
    ELSE
        'SELECT 1'
    END AS sql_statement
FROM pragma_table_info('users')
WHERE name = 'total_time';

-- Создаем таблицу для метрик поиска
CREATE TABLE IF NOT EXISTS search_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    search_id INTEGER NOT NULL,
    distance FLOAT DEFAULT 0,
    duration INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (search_id) REFERENCES search_operations(id)
);

COMMIT;
