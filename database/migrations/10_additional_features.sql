BEGIN TRANSACTION;

-- Таблица достижений
CREATE TABLE IF NOT EXISTS achievements (
    achievement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    icon TEXT NOT NULL,
    points INTEGER NOT NULL,
    category TEXT NOT NULL
);

-- Таблица пользовательских достижений
CREATE TABLE IF NOT EXISTS user_achievements (
    user_id INTEGER,
    achievement_id INTEGER,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, achievement_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (achievement_id) REFERENCES achievements(achievement_id)
);

-- Таблица рейтинга
CREATE TABLE IF NOT EXISTS user_ratings (
    user_id INTEGER PRIMARY KEY,
    rating_points INTEGER DEFAULT 0,
    total_operations INTEGER DEFAULT 0,
    successful_operations INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Таблица обучающих материалов
CREATE TABLE IF NOT EXISTS training_materials (
    material_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL,
    difficulty_level INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица прогресса обучения
CREATE TABLE IF NOT EXISTS user_training_progress (
    user_id INTEGER,
    material_id INTEGER,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    score INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, material_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (material_id) REFERENCES training_materials(material_id)
);

COMMIT;