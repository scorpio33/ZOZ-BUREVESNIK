from typing import Dict, Set
import re

class CallbackCollector:
    def __init__(self):
        self.found_callbacks: Set[str] = set()
        self.implemented_handlers: Set[str] = set()
        
    def collect_from_menu_handler(self, code: str):
        """Собирает callback_data из определений кнопок"""
        # Ищем все callback_data в определениях InlineKeyboardButton
        pattern = r'callback_data=["\']([^"\']+)["\']'
        callbacks = re.findall(pattern, code)
        self.found_callbacks.update(callbacks)
    
    def collect_from_handlers(self, code: str):
        """Собирает информацию о реализованных обработчиках"""
        # Ищем все обработки callback.data в условиях if/elif
        pattern = r'if\s+(?:query\.)?data\s*(?:==|\.startswith\(["\'])([\w_]+)'
        handlers = re.findall(pattern, code)
        self.implemented_handlers.update(handlers)
    
    def get_missing_handlers(self) -> Set[str]:
        """Возвращает список callback_data без обработчиков"""
        return self.found_callbacks - self.implemented_handlers
    
    def get_report(self) -> Dict[str, Set[str]]:
        return {
            'found_callbacks': self.found_callbacks,
            'implemented_handlers': self.implemented_handlers,
            'missing_handlers': self.get_missing_handlers()
        }
    
    def verify_callbacks(self) -> Dict[str, bool]:
        """Проверка соответствия callback_data и их обработчиков"""
        results = {}
        for callback in self.found_callbacks:
            has_handler = callback in self.implemented_handlers
            results[callback] = has_handler
            if not has_handler:
                print(f"Warning: No handler found for callback '{callback}'")
        return results
