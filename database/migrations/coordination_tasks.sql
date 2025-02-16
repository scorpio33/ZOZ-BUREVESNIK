-- Таблица шаблонов задач
CREATE TABLE IF NOT EXISTS task_templates (
    template_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    priority_level INTEGER DEFAULT 2,
    estimated_time INTEGER,
    category TEXT,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

-- Таблица напоминаний о задачах
CREATE TABLE IF NOT EXISTS task_reminders (
    reminder_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    reminder_time TIMESTAMP NOT NULL,
    reminder_type TEXT NOT NULL, -- before_deadline, status_update, custom
    reminder_text TEXT,
    is_sent BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (task_id) REFERENCES coordination_tasks(task_id)
);

-- Обновление таблицы задач
ALTER TABLE coordination_tasks ADD COLUMN template_id INTEGER REFERENCES task_templates(template_id);
ALTER TABLE coordination_tasks ADD COLUMN last_reminder_at TIMESTAMP;