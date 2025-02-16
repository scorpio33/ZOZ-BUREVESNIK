class LoadMonitor:
    def __init__(self):
        self.thresholds = SCALING_THRESHOLDS
        self.current_stats = {
            'users': 0,
            'operations': 0,
            'database': {
                'size': 0,
                'transactions': 0,
                'connections': 0
            }
        }

    async def check_load(self):
        """Проверка текущей нагрузки"""
        warnings = []
        
        if self.current_stats['users'] >= self.thresholds['users']['warning']:
            warnings.append({
                'type': 'users',
                'current': self.current_stats['users'],
                'threshold': self.thresholds['users']['warning'],
                'action': 'Consider database migration to PostgreSQL'
            })
            
        if self.current_stats['database']['transactions'] >= self.thresholds['database']['transactions_warning']:
            warnings.append({
                'type': 'transactions',
                'current': self.current_stats['database']['transactions'],
                'threshold': self.thresholds['database']['transactions_warning'],
                'action': 'Implement additional caching'
            })
            
        return warnings