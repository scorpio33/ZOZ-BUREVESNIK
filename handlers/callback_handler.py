from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

class CallbackHandler:
    def __init__(self, handlers_map):
        self.handlers = handlers_map
        self.navigation_history = {}  # user_id: [states]

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Центральный обработчик всех callback-запросов"""
        query = update.callback_query
        user_id = update.effective_user.id
        data = query.data
        
        logger.debug(f"Handling callback: {data} from user {user_id}")
        
        try:
            # Определяем тип callback и соответствующий обработчик
            handler_type = data.split('_')[0]
            if handler_type in self.handlers:
                await self.handlers[handler_type].handle_callback(update, context)
            else:
                logger.warning(f"Unknown callback type: {handler_type}")
                await query.answer("Функция временно недоступна")
                
        except Exception as e:
            logger.error(f"Error handling callback {data}: {e}")
            await query.answer("Произошла ошибка. Попробуйте еще раз")
            
        finally:
            await query.answer()