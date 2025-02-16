-- Базовые права для координаторов
INSERT OR IGNORE INTO coordinator_permissions (coordinator_id, permission, granted_by)
SELECT user_id, 'create_operation', 1
FROM users
WHERE coordinator_level > 0;

INSERT OR IGNORE INTO coordinator_permissions (coordinator_id, permission, granted_by)
SELECT user_id, 'manage_tasks', 1
FROM users
WHERE coordinator_level > 0;

INSERT OR IGNORE INTO coordinator_permissions (coordinator_id, permission, granted_by)
SELECT user_id, 'view_statistics', 1
FROM users
WHERE coordinator_level > 0;

-- Создание индексов для оптимизации
CREATE INDEX IF NOT EXISTS idx_permissions_type ON coordinator_permissions(permission);
