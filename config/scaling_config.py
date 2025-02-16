SCALING_THRESHOLDS = {
    'users': {
        'warning': 800,  # предупреждение при достижении
        'critical': 1200,  # необходимо масштабирование
        'max': 1500  # максимальная нагрузка
    },
    'operations': {
        'warning': 40,
        'critical': 60,
        'max': 70
    },
    'database': {
        'size_warning': 1024 * 1024 * 1024 * 10,  # 10 GB
        'transactions_warning': 1500,  # транзакций в секунду
        'connections_warning': 80  # одновременных подключений
    }
}

SCALING_ACTIONS = {
    'database_migration': {
        'type': 'postgres',
        'trigger_threshold': 1200,  # пользователей
        'preparation_time': 48,  # часов
        'required_resources': [
            'postgres_server',
            'backup_system',
            'migration_scripts'
        ]
    },
    'caching_upgrade': {
        'type': 'redis_cluster',
        'trigger_threshold': 900,  # пользователей
        'nodes': 3
    }
}