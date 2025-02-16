-- Таблица задач с расширенной системой приоритетов
CREATE TABLE IF NOT EXISTS coordination_tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id INTEGER NOT NULL,
    group_id INTEGER,
    creator_id INTEGER NOT NULL,
    assigned_to INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    priority_level INTEGER NOT NULL DEFAULT 1, -- 1: Низкий, 2: Средний, 3: Высокий, 4: Критический
    status TEXT DEFAULT 'pending', -- pending, in_progress, completed, cancelled
    deadline TIMESTAMP,
    estimated_time INTEGER, -- в минутах
    resources_needed TEXT, -- JSON с необходимыми ресурсами
    completion_percentage INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (operation_id) REFERENCES search_operations(operation_id),
    FOREIGN KEY (group_id) REFERENCES search_groups(group_id),
    FOREIGN KEY (creator_id) REFERENCES users(user_id),
    FOREIGN KEY (assigned_to) REFERENCES users(user_id)
);

-- Таблица для отслеживания прогресса и отчетности
CREATE TABLE IF NOT EXISTS task_progress (
    progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    reporter_id INTEGER NOT NULL,
    status_update TEXT,
    progress_percentage INTEGER,
    resources_used TEXT, -- JSON с использованными ресурсами
    report_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location TEXT, -- JSON с координатами
    attachments TEXT, -- JSON с ссылками на прикрепленные файлы
    FOREIGN KEY (task_id) REFERENCES coordination_tasks(task_id),
    FOREIGN KEY (reporter_id) REFERENCES users(user_id)
);

-- Таблица для управления ресурсами
CREATE TABLE IF NOT EXISTS operation_resources (
    resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id INTEGER NOT NULL,
    resource_type TEXT NOT NULL, -- equipment, personnel, vehicle, etc.
    resource_name TEXT NOT NULL,
    quantity INTEGER,
    status TEXT DEFAULT 'available', -- available, in_use, maintenance
    assigned_to INTEGER, -- task_id или group_id
    location TEXT, -- JSON с текущими координатами
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operation_id) REFERENCES search_operations(operation_id)
);