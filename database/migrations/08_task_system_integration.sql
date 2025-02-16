-- Добавление прав для координаторов
INSERT OR IGNORE INTO coordinator_permissions (coordinator_id, permission, granted_by)
SELECT user_id, 'manage_tasks', 1
FROM users
WHERE coordinator_level > 0;

-- Добавление базовых шаблонов задач
INSERT OR IGNORE INTO task_templates (
    title, description, priority_level, estimated_time, category, created_by
) VALUES 
    ('Обход сектора', 'Выполнить обход выделенного сектора поиска', 2, 120, 'search', 1),
    ('Проверка снаряжения', 'Проверить наличие и состояние поискового снаряжения', 1, 30, 'equipment', 1),
    ('Координация группы', 'Координация действий поисковой группы в секторе', 3, 240, 'coordination', 1);

-- Создание индексов для оптимизации
CREATE INDEX IF NOT EXISTS idx_tasks_status ON coordination_tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_deadline ON coordination_tasks(deadline);
CREATE INDEX IF NOT EXISTS idx_reminders_time ON task_reminders(reminder_time, is_sent);