-- Откат миграции v1.0.0

-- Удаляем индексы
DROP INDEX IF EXISTS idx_users_status;
DROP INDEX IF EXISTS idx_settings_key;

-- Удаляем таблицы
DROP TABLE IF EXISTS settings;
DROP TABLE IF EXISTS users;