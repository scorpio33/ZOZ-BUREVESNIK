-- Групповые чаты
CREATE TABLE IF NOT EXISTS group_chats (
    chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    type TEXT CHECK(type IN ('general', 'operational', 'emergency')) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES search_groups(group_id) ON DELETE CASCADE
);

-- Сообщения
CREATE TABLE IF NOT EXISTS messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    message_type TEXT CHECK(type IN ('text', 'location', 'file', 'command', 'emergency')) NOT NULL,
    content TEXT NOT NULL,
    is_pinned BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES group_chats(chat_id),
    FOREIGN KEY (sender_id) REFERENCES users(user_id)
);

-- Статусы участников
CREATE TABLE IF NOT EXISTS member_statuses (
    user_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    status TEXT CHECK(status IN ('active', 'resting', 'unavailable', 'emergency')) NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, group_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (group_id) REFERENCES search_groups(group_id)
);

-- Быстрые команды
CREATE TABLE IF NOT EXISTS quick_commands (
    command_id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    command TEXT NOT NULL,
    description TEXT,
    created_by INTEGER NOT NULL,
    FOREIGN KEY (group_id) REFERENCES search_groups(group_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

-- Создание индексов
CREATE INDEX IF NOT EXISTS idx_messages_chat ON messages(chat_id, created_at);
CREATE INDEX IF NOT EXISTS idx_member_statuses ON member_statuses(group_id, status);