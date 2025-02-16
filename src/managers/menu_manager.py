class MenuManager:
    def __init__(self):
        self.menus = {
            'main': {
                'text': "Главное меню",
                'buttons': [
                    ["🗺 Поиск", "📊 Статистика"],
                    ["⚙️ Настройки", "📍 Карта"]
                ]
            },
            'search': {
                'text': "Меню поиска",
                'buttons': [
                    ["Начать поиск", "Присоединиться к поиску"],
                    ["Координация", "Назад"]
                ]
            }
            # Add other menus here
        }

    def get_menu(self, menu_id: str):
        """Get menu text and keyboard for given menu ID"""
        menu = self.menus.get(menu_id.replace('_menu', ''), self.menus['main'])
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text, callback_data=f"{menu_id}_{i}_{j}")
             for j, text in enumerate(row)]
            for i, row in enumerate(menu['buttons'])
        ])
        return menu['text'], keyboard