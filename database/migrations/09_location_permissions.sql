-- Миграция для прав доступа к геолокации
BEGIN TRANSACTION;

-- Добавляем базовые права на геолокацию для всех пользователей
CREATE TABLE IF NOT EXISTS location_permissions (
    user_id INTEGER NOT NULL,
    permission_type TEXT NOT NULL,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, permission_type),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Добавляем базовые разрешения для существующих пользователей
INSERT OR IGNORE INTO location_permissions (user_id, permission_type)
SELECT user_id, 'share_location'
FROM users;

INSERT OR IGNORE INTO location_permissions (user_id, permission_type)
SELECT user_id, 'view_location'
FROM users;

-- Создаем индекс для оптимизации
CREATE INDEX IF NOT EXISTS idx_location_permissions ON location_permissions(user_id);

COMMIT;