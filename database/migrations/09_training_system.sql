-- Таблица учебных материалов
CREATE TABLE IF NOT EXISTS training_materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    content TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('theory', 'practice', 'test')),
    required_level INTEGER DEFAULT 1,
    points INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица прогресса обучения пользователей
CREATE TABLE IF NOT EXISTS user_training_progress (
    user_id INTEGER,
    material_id INTEGER,
    status TEXT DEFAULT 'not_started' CHECK (status IN ('not_started', 'in_progress', 'completed')),
    score INTEGER DEFAULT 0,
    attempts INTEGER DEFAULT 0,
    completed_at TIMESTAMP,
    PRIMARY KEY (user_id, material_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (material_id) REFERENCES training_materials(id)
);

-- Таблица тестовых вопросов
CREATE TABLE IF NOT EXISTS training_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_id INTEGER,
    question TEXT NOT NULL,
    options TEXT NOT NULL, -- JSON array of options
    correct_answer INTEGER NOT NULL,
    explanation TEXT,
    FOREIGN KEY (material_id) REFERENCES training_materials(id)
);

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_training_materials_level ON training_materials(required_level);
CREATE INDEX IF NOT EXISTS idx_user_training_status ON user_training_progress(user_id, status);