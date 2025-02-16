-- Партиционирование таблицы location_history по времени
CREATE TABLE IF NOT EXISTS location_history_partitioned (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    operation_id INTEGER
) PARTITION BY RANGE (strftime('%Y%m', timestamp));

-- Создание партиций по месяцам
CREATE TABLE location_history_y2023m12 
PARTITION OF location_history_partitioned 
FOR VALUES FROM ('202312') TO ('202401');

CREATE TABLE location_history_y2024m01 
PARTITION OF location_history_partitioned 
FOR VALUES FROM ('202401') TO ('202402');