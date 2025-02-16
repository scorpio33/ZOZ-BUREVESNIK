
-- Таблица для поисковых групп
CREATE TABLE IF NOT EXISTS search_groups (
    group_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    leader_id INTEGER NOT NULL,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (leader_id) REFERENCES users(user_id)
);

-- Таблица для участников групп
CREATE TABLE IF NOT EXISTS group_members (
    group_id INTEGER,
    user_id INTEGER,
    role TEXT DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES search_groups(group_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Индексы
CREATE INDEX IF NOT EXISTS idx_groups_status ON search_groups(status);
CREATE INDEX IF NOT EXISTS idx_groups_leader ON search_groups(leader_id);
