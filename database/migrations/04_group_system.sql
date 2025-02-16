
-- Таблица для задач поисковых групп
CREATE TABLE IF NOT EXISTS coordination_tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',
    priority INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deadline TIMESTAMP,
    completed_at TIMESTAMP,
    created_by INTEGER NOT NULL,
    assigned_to INTEGER,
    FOREIGN KEY (group_id) REFERENCES search_groups(group_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id),
    FOREIGN KEY (assigned_to) REFERENCES users(user_id)
);

-- Таблица для прогресса выполнения задач
CREATE TABLE IF NOT EXISTS task_progress (
    progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    status_update TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER NOT NULL,
    FOREIGN KEY (task_id) REFERENCES coordination_tasks(task_id),
    FOREIGN KEY (updated_by) REFERENCES users(user_id)
);

-- Индексы
CREATE INDEX IF NOT EXISTS idx_tasks_status ON coordination_tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_group ON coordination_tasks(group_id);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON coordination_tasks(assigned_to);
