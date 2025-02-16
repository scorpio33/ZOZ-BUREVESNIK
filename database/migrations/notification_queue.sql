-- Таблица очереди уведомлений
CREATE TABLE IF NOT EXISTS notification_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    priority INTEGER DEFAULT 2,
    status TEXT DEFAULT 'pending',
    scheduled_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_notification_queue_status 
ON notification_queue(status);

CREATE INDEX IF NOT EXISTS idx_notification_queue_scheduled 
ON notification_queue(scheduled_time);