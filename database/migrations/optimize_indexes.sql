-- Индексы для оптимизации поиска по времени
CREATE INDEX IF NOT EXISTS idx_operations_time 
ON search_operations(start_time, end_time);

-- Составной индекс для задач
CREATE INDEX IF NOT EXISTS idx_tasks_complex 
ON coordination_tasks(status, priority_level, deadline);

-- Индекс для поиска по геолокации
CREATE INDEX IF NOT EXISTS idx_location_coords 
ON live_positions(latitude, longitude);

-- Индекс для поиска пользователей по уровню
CREATE INDEX IF NOT EXISTS idx_users_level 
ON users(level, experience);

-- Индекс для поиска по статусу координатора
CREATE INDEX IF NOT EXISTS idx_coordinator_status 
ON coordinators(status, level);