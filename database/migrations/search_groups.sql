-- Таблица поисковых операций
CREATE TABLE IF NOT EXISTS search_operations (
    operation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    coordinator_id INTEGER NOT NULL,
    status TEXT DEFAULT 'active',
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    description TEXT,
    location TEXT,  -- JSON с координатами центра операции
    FOREIGN KEY (coordinator_id) REFERENCES users(user_id)
);

-- Таблица поисковых групп
CREATE TABLE IF NOT EXISTS search_groups (
    group_id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    leader_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    max_members INTEGER DEFAULT 10,
    current_sector TEXT,
    current_location JSON,
    equipment_required JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operation_id) REFERENCES search_operations(operation_id),
    FOREIGN KEY (leader_id) REFERENCES users(user_id)
);

-- Таблица участников групп
CREATE TABLE IF NOT EXISTS group_members (
    member_id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    last_location JSON,
    last_active TIMESTAMP,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES search_groups(group_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Таблица заданий для групп
CREATE TABLE IF NOT EXISTS group_tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT DEFAULT 'normal',
    status TEXT DEFAULT 'pending',
    assigned_to INTEGER,
    location JSON,
    deadline TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES search_groups(group_id),
    FOREIGN KEY (assigned_to) REFERENCES users(user_id)
);

-- Таблица для отслеживания перемещений
CREATE TABLE IF NOT EXISTS location_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    location JSON NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (group_id) REFERENCES search_groups(group_id)
);

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_operations_coordinator ON search_operations(coordinator_id);
CREATE INDEX IF NOT EXISTS idx_operations_status ON search_operations(status);
CREATE INDEX IF NOT EXISTS idx_groups_operation ON search_groups(operation_id);
CREATE INDEX IF NOT EXISTS idx_groups_leader ON search_groups(leader_id);
CREATE INDEX IF NOT EXISTS idx_groups_status ON search_groups(status);
CREATE INDEX IF NOT EXISTS idx_members_group ON group_members(group_id);
CREATE INDEX IF NOT EXISTS idx_members_user ON group_members(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_group ON group_tasks(group_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON group_tasks(status);
CREATE INDEX IF NOT EXISTS idx_location_user ON location_history(user_id);
CREATE INDEX IF NOT EXISTS idx_location_group ON location_history(group_id);
