-- Создание основной таблицы coordination_tasks, если она не существует
CREATE TABLE IF NOT EXISTS coordination_tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    creator_id INTEGER NOT NULL,
    assigned_to INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    priority_level INTEGER DEFAULT 1,
    deadline TIMESTAMP,
    notifications_sent INTEGER DEFAULT 0,
    subtasks_count INTEGER DEFAULT 0,
    parent_task_id INTEGER DEFAULT NULL,
    estimated_time INTEGER,
    FOREIGN KEY (group_id) REFERENCES search_groups(group_id),
    FOREIGN KEY (creator_id) REFERENCES users(user_id),
    FOREIGN KEY (assigned_to) REFERENCES users(user_id),
    FOREIGN KEY (parent_task_id) REFERENCES coordination_tasks(task_id)
);

-- Таблица для зависимостей задач
CREATE TABLE IF NOT EXISTS task_dependencies (
    dependency_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    dependent_task_id INTEGER NOT NULL,
    dependency_type TEXT NOT NULL,
    FOREIGN KEY (task_id) REFERENCES coordination_tasks(task_id),
    FOREIGN KEY (dependent_task_id) REFERENCES coordination_tasks(task_id)
);

-- Таблица для отслеживания прогресса задач
CREATE TABLE IF NOT EXISTS task_progress (
    progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    status_change TEXT NOT NULL,
    changed_by INTEGER NOT NULL,
    comment TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES coordination_tasks(task_id),
    FOREIGN KEY (changed_by) REFERENCES users(user_id)
);

-- Таблица для уведомлений о задачах
CREATE TABLE IF NOT EXISTS task_notifications (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES coordination_tasks(task_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Создание индексов для оптимизации
CREATE INDEX IF NOT EXISTS idx_task_progress_task_id ON task_progress(task_id);
CREATE INDEX IF NOT EXISTS idx_task_notifications_user_id ON task_notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_task_notifications_task_id ON task_notifications(task_id);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON coordination_tasks(priority_level);
CREATE INDEX IF NOT EXISTS idx_tasks_deadline ON coordination_tasks(deadline);
