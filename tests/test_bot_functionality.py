import asyncio
import logging
from telegram import Update
from telegram.ext import ContextTypes
from unittest.mock import AsyncMock, MagicMock

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BotTester:
    def __init__(self, bot):
        self.bot = bot
        self.test_user_id = 123456789
        self.setup_mocks()

    def setup_mocks(self):
        """Настройка моков для тестирования"""
        self.update = MagicMock(spec=Update)
        self.context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        self.query = AsyncMock()
        self.message = AsyncMock()
        
        # Настройка моков
        self.update.effective_user.id = self.test_user_id
        self.update.callback_query = self.query
        self.query.message = self.message
        self.context.user_data = {}

    async def test_start_menu(self):
        """Тест стартового меню"""
        logger.info("Testing start menu...")
        
        # Тест команды /start
        self.update.message = AsyncMock()
        self.update.message.text = "/start"
        await self.bot.start_command(self.update, self.context)
        
        # Проверка кнопок стартового меню
        buttons_to_test = ['auth', 'donate', 'about']
        for button in buttons_to_test:
            self.query.data = button
            await self.bot.callback_manager.handle_callback(self.update, self.context)

    async def test_auth_flow(self):
        """Тест процесса авторизации"""
        logger.info("Testing authentication...")
        
        # Тест авторизации
        self.query.data = "auth"
        await self.bot.callback_manager.handle_callback(self.update, self.context)
        
        # Тест ввода пароля
        self.update.message.text = "correct_password"
        await self.bot.auth_handler.check_password(self.update, self.context)

    async def test_main_menu(self):
        """Тест главного меню"""
        logger.info("Testing main menu...")
        
        # Установка авторизованного состояния
        self.context.user_data['authorized'] = True
        
        # Тест кнопок главного меню
        main_menu_buttons = [
            'search_menu', 'stats_menu', 'settings_menu', 'map_menu'
        ]
        
        for button in main_menu_buttons:
            self.query.data = button
            await self.bot.callback_manager.handle_callback(self.update, self.context)

    async def test_search_functionality(self):
        """Тест функционала поиска"""
        logger.info("Testing search functionality...")
        
        search_buttons = [
            'search_start', 'search_join', 'search_coordination'
        ]
        
        for button in search_buttons:
            self.query.data = button
            await self.bot.callback_manager.handle_callback(self.update, self.context)

    async def test_map_functionality(self):
        """Тест функционала карты"""
        logger.info("Testing map functionality...")
        
        map_buttons = [
            'start_track', 'stop_track', 'show_tracks', 'send_location'
        ]
        
        for button in map_buttons:
            self.query.data = button
            await self.bot.callback_manager.handle_callback(self.update, self.context)

    async def test_error_handling(self):
        """Тест обработки ошибок"""
        logger.info("Testing error handling...")
        
        # Тест обработки несуществующего callback
        self.query.data = "nonexistent_callback"
        await self.bot.callback_manager.handle_callback(self.update, self.context)
        
        # Тест доступа к защищенному функционалу без авторизации
        self.context.user_data['authorized'] = False
        self.query.data = "search_menu"
        await self.bot.callback_manager.handle_callback(self.update, self.context)

    async def test_all_callbacks(self):
        """Тест всех callback'ов"""
        collector = CallbackCollector()
        
        # Собираем все callback'и из меню
        collector.collect_from_menu_handler(self.bot.menu_manager.get_menu_code())
        
        # Собираем все обработчики
        collector.collect_from_handlers(self.bot.callback_manager.get_handlers_code())
        
        # Проверяем соответствие
        results = collector.verify_callbacks()
        
        # Проверяем, что все callback'и имеют обработчики
        missing_handlers = [cb for cb, has_handler in results.items() if not has_handler]
        self.assertEqual(missing_handlers, [], f"Missing handlers for callbacks: {missing_handlers}")

    async def run_all_tests(self):
        """Запуск всех тестов"""
        tests = [
            self.test_start_menu,
            self.test_auth_flow,
            self.test_main_menu,
            self.test_search_functionality,
            self.test_map_functionality,
            self.test_error_handling,
            self.test_all_callbacks
        ]
        
        for test in tests:
            try:
                await test()
                logger.info(f"✅ {test.__name__} passed")
            except Exception as e:
                logger.error(f"❌ {test.__name__} failed: {str(e)}")
                raise

async def run_tests(bot):
    tester = BotTester(bot)
    await tester.run_all_tests()

if __name__ == "__main__":
    from main import bot
    asyncio.run(run_tests(bot))
