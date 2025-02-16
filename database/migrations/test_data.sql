-- Тестовые данные для разработки

-- Тестовые пользователи
INSERT INTO users (user_id, username, first_name, last_name, status) VALUES
    (1, 'admin', 'Admin', 'User', 'admin'),
    (2, 'coordinator1', 'John', 'Doe', 'coordinator'),
    (3, 'user1', 'Jane', 'Smith', 'user'),
    (4, 'user2', 'Bob', 'Johnson', 'user');

-- Базовые настройки
INSERT INTO settings (key, value, description) VALUES
    ('welcome_message', 'Добро пожаловать в бот!', 'Приветственное сообщение'),
    ('max_group_size', '10', 'Максимальный размер группы'),
    ('default_radius', '5000', 'Радиус поиска по умолчанию (в метрах)');