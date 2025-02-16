
-- Создаем временную таблицу только с базовыми колонками
CREATE TABLE IF NOT EXISTS temp_users AS 
SELECT 
    user_id,
    username,
    status,
    experience,
    created_at
FROM users;

-- Удаляем старую таблицу
DROP TABLE users;

-- Создаем новую таблицу с обновленной структурой
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    status TEXT DEFAULT 'user',
    experience INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    coordinator_level INTEGER DEFAULT 0,
    can_create_operations BOOLEAN DEFAULT FALSE
);

-- Копируем базовые данные обратно
INSERT INTO users (
    user_id,
    username,
    status,
    experience,
    created_at
)
SELECT 
    user_id,
    username,
    COALESCE(status, 'user'),
    COALESCE(experience, 0),
    created_at
FROM temp_users;

-- Удаляем временную таблицу
DROP TABLE temp_users;

-- Таблица для отслеживания эскалаций
CREATE TABLE IF NOT EXISTS task_escalations (
    escalation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    escalation_level INTEGER NOT NULL DEFAULT 1,
    escalated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolved_by INTEGER,
    resolution_notes TEXT,
    FOREIGN KEY (task_id) REFERENCES coordination_tasks(task_id),
    FOREIGN KEY (resolved_by) REFERENCES users(user_id)
);

-- Таблица для прав доступа координаторов
CREATE TABLE IF NOT EXISTS coordinator_permissions (
    coordinator_id INTEGER NOT NULL,
    permission TEXT NOT NULL,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    granted_by INTEGER,
    PRIMARY KEY (coordinator_id, permission),
    FOREIGN KEY (coordinator_id) REFERENCES users(user_id),
    FOREIGN KEY (granted_by) REFERENCES users(user_id)
);

-- Индексы
CREATE INDEX IF NOT EXISTS idx_escalations_task ON task_escalations(task_id);
CREATE INDEX IF NOT EXISTS idx_permissions_coordinator ON coordinator_permissions(coordinator_id);
