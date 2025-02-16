-- Таблица шаблонов задач
CREATE TABLE IF NOT EXISTS task_templates (
    template_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    priority_level INTEGER DEFAULT 1,
    estimated_time INTEGER,
    category TEXT,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

-- Таблица для хранения напоминаний
CREATE TABLE IF NOT EXISTS task_reminders (
    reminder_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    reminder_time TIMESTAMP NOT NULL,
    reminder_type TEXT NOT NULL, -- 'deadline', 'custom'
    is_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES coordination_tasks(task_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Таблица статистики задач
CREATE TABLE IF NOT EXISTS task_statistics (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    completion_time INTEGER, -- в минутах
    actual_start_time TIMESTAMP,
    actual_end_time TIMESTAMP,
    deviation_from_estimate INTEGER, -- в минутах
    FOREIGN KEY (task_id) REFERENCES coordination_tasks(task_id)
);

-- Индексы
CREATE INDEX IF NOT EXISTS idx_reminders_time ON task_reminders(reminder_time);
CREATE INDEX IF NOT EXISTS idx_task_stats_completion ON task_statistics(completion_time);