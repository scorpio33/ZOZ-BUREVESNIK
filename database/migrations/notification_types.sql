-- Обновление таблицы очереди уведомлений
ALTER TABLE notification_queue 
ADD COLUMN notification_type TEXT NOT NULL DEFAULT 'info';

-- Таблица для хранения напоминаний
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    remind_at TIMESTAMP NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Индекс для оптимизации поиска напоминаний
CREATE INDEX IF NOT EXISTS idx_reminders_remind_at 
ON reminders(remind_at);