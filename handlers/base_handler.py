from abc import ABC, abstractmethod
from telegram import Update
from telegram.ext import ContextTypes

class BaseHandler:
    def __init__(self, db_manager):
        """
        Initialize base handler
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle updates. Must be implemented by subclasses.
        
        Args:
            update: Update from Telegram
            context: CallbackContext
            
        Returns:
            bool: True if handled, False otherwise
        """
        raise NotImplementedError("Subclasses must implement handle()")
