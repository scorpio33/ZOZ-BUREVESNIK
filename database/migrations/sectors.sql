-- Таблица секторов поиска
CREATE TABLE IF NOT EXISTS search_sectors (
    sector_id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    boundaries TEXT NOT NULL,  -- GeoJSON полигон
    status TEXT DEFAULT 'pending',  -- pending/in_progress/completed
    progress FLOAT DEFAULT 0,
    priority INTEGER DEFAULT 1,
    difficulty TEXT DEFAULT 'normal',
    terrain_type TEXT,
    assigned_team INTEGER,
    last_searched TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (operation_id) REFERENCES search_operations(operation_id),
    FOREIGN KEY (assigned_team) REFERENCES search_teams(team_id)
);

-- Таблица для отслеживания прогресса поиска в секторах
CREATE TABLE IF NOT EXISTS sector_progress (
    progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sector_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    coverage_percent FLOAT DEFAULT 0,
    search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (sector_id) REFERENCES search_sectors(sector_id),
    FOREIGN KEY (team_id) REFERENCES search_teams(team_id)
);

-- Таблица поисковых команд, если её ещё нет
CREATE TABLE IF NOT EXISTS search_teams (
    team_id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    leader_id INTEGER NOT NULL,
    status TEXT DEFAULT 'active',
    current_sector INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operation_id) REFERENCES search_operations(operation_id),
    FOREIGN KEY (leader_id) REFERENCES users(user_id),
    FOREIGN KEY (current_sector) REFERENCES search_sectors(sector_id)
);

-- Таблица поисковых операций, если её ещё нет
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

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_sectors_status ON search_sectors(status);
CREATE INDEX IF NOT EXISTS idx_sectors_priority ON search_sectors(priority);
CREATE INDEX IF NOT EXISTS idx_sectors_operation ON search_sectors(operation_id);
CREATE INDEX IF NOT EXISTS idx_sector_progress_sector ON sector_progress(sector_id);
CREATE INDEX IF NOT EXISTS idx_sector_progress_team ON sector_progress(team_id);
CREATE INDEX IF NOT EXISTS idx_teams_operation ON search_teams(operation_id);
CREATE INDEX IF NOT EXISTS idx_teams_leader ON search_teams(leader_id);
CREATE INDEX IF NOT EXISTS idx_operations_coordinator ON search_operations(coordinator_id);
CREATE INDEX IF NOT EXISTS idx_operations_status ON search_operations(status);
