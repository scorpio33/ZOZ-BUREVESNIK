def audit_map_search_callbacks():
    """Аудит callback'ов для модулей карты и поиска"""
    map_callbacks = {
        'map_main': 'Главное меню карты',
        'start_track': 'Начать запись трека',
        'stop_track': 'Завершить запись трека',
        'my_tracks': 'Мои треки',
        'send_location': 'Отправить местоположение',
        'online_map': 'Карта онлайн'
    }
    
    search_callbacks = {
        'search_main': 'Главное меню поиска',
        'start_search': 'Начать поиск',
        'join_search': 'Присоединиться к поиску',
        'coordination': 'Координация',
        'coord_sectors': 'Управление секторами',
        'coord_teams': 'Управление командами',
        'coord_tasks': 'Задачи',
        'coord_mark_point': 'Отметить точку'
    }
    
    return map_callbacks, search_callbacks