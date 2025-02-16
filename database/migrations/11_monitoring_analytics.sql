-- Таблица метрик эффективности операций
CREATE TABLE IF NOT EXISTS operation_metrics (
    operation_id INTEGER PRIMARY KEY,
    response_time INTEGER, -- время реагирования в минутах
    coordination_score FLOAT, -- оценка координации (0-100)
    resource_efficiency FLOAT, -- эффективность использования ресурсов (0-100)
    coverage_rate FLOAT, -- процент покрытия территории
    success_rate FLOAT, -- процент успешности
    total_distance FLOAT, -- общая пройденная дистанция
    total_time INTEGER, -- общее время операции в минутах
    team_performance FLOAT, -- эффективность команды (0-100)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operation_id) REFERENCES search_operations(operation_id)
);

-- Таблица временных меток операции
CREATE TABLE IF NOT EXISTS operation_timestamps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id INTEGER,
    event_type TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT,
    FOREIGN KEY (operation_id) REFERENCES search_operations(operation_id)
);

-- Таблица эффективности команд
CREATE TABLE IF NOT EXISTS team_performance_metrics (
    team_id INTEGER,
    operation_id INTEGER,
    coverage_area FLOAT, -- покрытая площадь
    task_completion_rate FLOAT, -- процент выполнения задач
    coordination_score FLOAT, -- оценка координации
    response_time INTEGER, -- время реагирования
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (team_id, operation_id),
    FOREIGN KEY (team_id) REFERENCES search_groups(group_id),
    FOREIGN KEY (operation_id) REFERENCES search_operations(operation_id)
);

-- Представление для агрегированной статистики
CREATE VIEW IF NOT EXISTS operation_analytics AS
SELECT 
    o.operation_id,
    o.status,
    om.response_time,
    om.coordination_score,
    om.success_rate,
    COUNT(DISTINCT sg.group_id) as team_count,
    COUNT(DISTINCT gm.user_id) as participant_count,
    AVG(tpm.task_completion_rate) as avg_task_completion,
    SUM(tpm.coverage_area) as total_coverage_area
FROM search_operations o
LEFT JOIN operation_metrics om ON o.operation_id = om.operation_id
LEFT JOIN search_groups sg ON o.operation_id = sg.operation_id
LEFT JOIN group_members gm ON sg.group_id = gm.group_id
LEFT JOIN team_performance_metrics tpm ON sg.group_id = tpm.team_id
GROUP BY o.operation_id;