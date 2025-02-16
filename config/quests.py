from typing import Dict

QUEST_CATEGORIES = {
    'training': '📚 Обучение',
    'search': '🔍 Поиски',
    'coordination': '👥 Координация',
    'special': '⭐️ Особые'
}

QUEST_TYPES = {
    'one_time': 'Одноразовый',
    'daily': 'Ежедневный',
    'weekly': 'Еженедельный',
    'achievement': 'Достижение'
}

QUESTS: Dict[str, Dict] = {
    # Обучающие квесты
    'complete_training': {
        'category': 'training',
        'title': '🎓 Пройти обучение',
        'description': 'Завершите базовый курс обучения',
        'type': 'one_time',
        'required_level': 1,
        'reward_exp': 100,
        'reward_coins': 50,
        'steps': ['theory', 'practice', 'exam']
    },
    
    # Поисковые квесты
    'first_search': {
        'category': 'search',
        'title': '🔍 Первый поиск',
        'description': 'Примите участие в первой поисковой операции',
        'type': 'one_time',
        'required_level': 2,
        'reward_exp': 200,
        'reward_coins': 100,
        'conditions': {'searches_completed': 1}
    },
    'track_master': {
        'category': 'search',
        'title': '📍 Мастер треков',
        'description': 'Запишите 5 треков во время поисков',
        'type': 'achievement',
        'required_level': 3,
        'reward_exp': 300,
        'reward_coins': 150,
        'conditions': {'tracks_recorded': 5}
    },
    
    # Координационные квесты
    'team_leader': {
        'category': 'coordination',
        'title': '👑 Лидер команды',
        'description': 'Успешно завершите поиск в роли координатора',
        'type': 'achievement',
        'required_level': 5,
        'reward_exp': 500,
        'reward_coins': 250,
        'conditions': {'successful_coordinations': 1}
    },
    
    # Особые квесты
    'night_search': {
        'category': 'special',
        'title': '🌙 Ночной поиск',
        'description': 'Участвуйте в ночной поисковой операции',
        'type': 'achievement',
        'required_level': 4,
        'reward_exp': 400,
        'reward_coins': 200,
        'conditions': {'night_searches': 1}
    }
}

# Уровни и награды
LEVEL_THRESHOLDS = {
    1: 0,
    2: 100,
    3: 300,
    4: 600,
    5: 1000,
    6: 1500,
    7: 2100,
    8: 2800,
    9: 3600,
    10: 4500
}

LEVEL_REWARDS = {
    2: {'coins': 100, 'title': 'Новичок'},
    5: {'coins': 300, 'title': 'Опытный'},
    8: {'coins': 500, 'title': 'Профессионал'},
    10: {'coins': 1000, 'title': 'Мастер'}
}
