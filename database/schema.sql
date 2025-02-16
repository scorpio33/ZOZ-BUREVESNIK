-- Основные таблицы

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    full_name TEXT,
    level INTEGER DEFAULT 1,
    experience INTEGER DEFAULT 0,
    is_coordinator BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quests (
    quest_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    reward_exp INTEGER DEFAULT 0,
    required_level INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quest_progress (
    user_id INTEGER,
    quest_id INTEGER,
    progress INTEGER DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (user_id, quest_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (quest_id) REFERENCES quests(quest_id)
);

CREATE TABLE IF NOT EXISTS operations (
    operation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    coordinator_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',
    location TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (coordinator_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS groups (
    group_id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id INTEGER,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operation_id) REFERENCES operations(operation_id)
);

CREATE TABLE IF NOT EXISTS tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',
    priority TEXT DEFAULT 'normal',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deadline TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups(group_id)
);

-- Таблица для хранения донатов
CREATE TABLE IF NOT EXISTS donations (
    donation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    transaction_id TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Таблица для хранения статусов пользователей
CREATE TABLE IF NOT EXISTS user_status (
    user_id INTEGER PRIMARY KEY,
    status TEXT NOT NULL,
    valid_until TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER PRIMARY KEY,
    role TEXT NOT NULL CHECK (role IN ('user', 'coordinator', 'admin', 'developer')),
    assigned_by INTEGER,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (assigned_by) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS role_permissions (
    role TEXT,
    permission TEXT,
    PRIMARY KEY (role, permission)
);

-- Таблица координационных задач
CREATE TABLE IF NOT EXISTS coordination_tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    creator_id INTEGER NOT NULL,
    assigned_to INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT DEFAULT 'normal',
    status TEXT DEFAULT 'pending',
    location TEXT,  -- JSON с координатами
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES search_groups(group_id),
    FOREIGN KEY (creator_id) REFERENCES users(user_id),
    FOREIGN KEY (assigned_to) REFERENCES users(user_id)
);

-- Таблица секторов поиска
CREATE TABLE IF NOT EXISTS search_sectors (
    sector_id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    boundaries TEXT NOT NULL,  -- GeoJSON полигон
    status TEXT DEFAULT 'pending',  -- pending/in_progress/completed
    assigned_team INTEGER,  -- ID команды, работающей в секторе
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES search_groups(group_id),
    FOREIGN KEY (assigned_team) REFERENCES search_teams(team_id)
);

-- Таблица поисковых команд
CREATE TABLE IF NOT EXISTS search_teams (
    team_id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    leader_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    current_sector INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES search_groups(group_id),
    FOREIGN KEY (leader_id) REFERENCES users(user_id),
    FOREIGN KEY (current_sector) REFERENCES search_sectors(sector_id)
);

-- Таблица участников команд
CREATE TABLE IF NOT EXISTS team_members (
    team_id INTEGER,
    user_id INTEGER,
    role TEXT DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (team_id, user_id),
    FOREIGN KEY (team_id) REFERENCES search_teams(team_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Таблица поисковых групп внутри операции
CREATE TABLE IF NOT EXISTS operation_groups (
    group_id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    leader_id INTEGER NOT NULL,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_report_time TIMESTAMP,
    current_sector_id INTEGER,
    FOREIGN KEY (operation_id) REFERENCES search_operations(operation_id),
    FOREIGN KEY (leader_id) REFERENCES users(user_id),
    FOREIGN KEY (current_sector_id) REFERENCES search_sectors(sector_id)
);

-- Таблица участников групп
CREATE TABLE IF NOT EXISTS operation_group_members (
    group_id INTEGER,
    user_id INTEGER,
    role TEXT DEFAULT 'member',  -- leader/member
    status TEXT DEFAULT 'active',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_location TEXT,  -- JSON с координатами
    last_active TIMESTAMP,
    PRIMARY KEY (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES operation_groups(group_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Таблица групповых сообщений
CREATE TABLE IF NOT EXISTS group_messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    message_type TEXT NOT NULL,  -- text/location/alert/report
    content TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_pinned BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (group_id) REFERENCES operation_groups(group_id),
    FOREIGN KEY (sender_id) REFERENCES users(user_id)
);

-- Обновление таблицы coordination_tasks
ALTER TABLE coordination_tasks ADD COLUMN priority_level INTEGER DEFAULT 1;
ALTER TABLE coordination_tasks ADD COLUMN deadline TIMESTAMP;
ALTER TABLE coordination_tasks ADD COLUMN notifications_sent INTEGER DEFAULT 0;

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

-- Таблица заявок на статус координатора
CREATE TABLE IF NOT EXISTS coordinator_requests (
    request_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    full_name TEXT NOT NULL,
    region TEXT NOT NULL,
    phone TEXT NOT NULL,
    team_name TEXT NOT NULL,
    position TEXT NOT NULL,
    search_count INTEGER NOT NULL,
    experience_time TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    processed_by INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (processed_by) REFERENCES users(user_id)
);

-- Таблица координаторов
CREATE TABLE IF NOT EXISTS coordinators (
    coordinator_id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE,
    status TEXT DEFAULT 'active',
    level INTEGER DEFAULT 1,
    rating FLOAT DEFAULT 0,
    total_operations INTEGER DEFAULT 0,
    successful_operations INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Таблица прав координаторов
CREATE TABLE IF NOT EXISTS coordinator_permissions (
    coordinator_id INTEGER NOT NULL,
    permission TEXT NOT NULL,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    granted_by INTEGER NOT NULL,
    PRIMARY KEY (coordinator_id, permission),
    FOREIGN KEY (coordinator_id) REFERENCES users(user_id),
    FOREIGN KEY (granted_by) REFERENCES users(user_id)
);

-- Добавляем поле is_coordinator в таблицу users, если его нет
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_coordinator BOOLEAN DEFAULT FALSE;
