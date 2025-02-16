-- Удаляем существующие таблицы, если они есть
DROP TABLE IF EXISTS search_areas;
DROP TABLE IF EXISTS group_members;

-- Таблица для областей поиска
CREATE TABLE IF NOT EXISTS search_areas (
    area_id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id INTEGER NOT NULL,
    boundaries TEXT NOT NULL,  -- GeoJSON
    metadata TEXT,            -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active',
    created_by INTEGER NOT NULL,
    FOREIGN KEY (operation_id) REFERENCES search_operations(operation_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

-- Таблица для участников групп с расширенными возможностями
CREATE TABLE IF NOT EXISTS group_members (
    user_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'paused', 'emergency')),
    role TEXT DEFAULT 'member' CHECK(role IN ('member', 'leader', 'coordinator')),
    last_location TEXT,  -- JSON
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    experience_level INTEGER DEFAULT 1,
    equipment_status TEXT DEFAULT 'ready' CHECK(equipment_status IN ('ready', 'partial', 'missing')),
    notes TEXT,
    PRIMARY KEY (user_id, group_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES search_groups(group_id) ON DELETE CASCADE
);

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_search_areas_operation ON search_areas(operation_id);
CREATE INDEX IF NOT EXISTS idx_search_areas_status ON search_areas(status);
CREATE INDEX IF NOT EXISTS idx_group_members_status ON group_members(status);
CREATE INDEX IF NOT EXISTS idx_group_members_role ON group_members(role);
CREATE INDEX IF NOT EXISTS idx_group_members_last_update ON group_members(last_update);

-- Триггер для автоматического обновления updated_at
CREATE TRIGGER IF NOT EXISTS update_search_areas_timestamp 
AFTER UPDATE ON search_areas
BEGIN
    UPDATE search_areas SET updated_at = CURRENT_TIMESTAMP
    WHERE area_id = NEW.area_id;
END;

-- Представление для активных участников групп
CREATE VIEW IF NOT EXISTS active_group_members AS
SELECT 
    gm.*,
    u.username,
    u.full_name,
    sg.name as group_name,
    sg.operation_id
FROM group_members gm
JOIN users u ON gm.user_id = u.user_id
JOIN search_groups sg ON gm.group_id = sg.group_id
WHERE gm.status = 'active';

-- Представление для статистики поисковых областей
CREATE VIEW IF NOT EXISTS search_areas_stats AS
SELECT 
    sa.area_id,
    sa.operation_id,
    sa.status,
    sa.created_at,
    u.username as created_by_user,
    COUNT(DISTINCT gm.user_id) as active_members,
    MAX(gm.last_update) as last_member_update
FROM search_areas sa
LEFT JOIN search_groups sg ON sa.operation_id = sg.operation_id
LEFT JOIN group_members gm ON sg.group_id = gm.group_id AND gm.status = 'active'
JOIN users u ON sa.created_by = u.user_id
GROUP BY sa.area_id;