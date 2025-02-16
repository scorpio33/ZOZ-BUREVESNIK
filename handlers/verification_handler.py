import logging
import random
import string
from datetime import datetime, timedelta
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.states import States
from utils.email_sender import EmailSender
from utils.phone_utils import PhoneUtils
from utils.security_utils import SecurityUtils
from config.settings import ALLOWED_DOCUMENT_TYPES, MAX_DOCUMENT_SIZE

logger = logging.getLogger(__name__)

class VerificationHandler:
    def __init__(self, db_manager):
        self.db = db_manager
        self.email_sender = EmailSender()
        self.phone_utils = PhoneUtils()
        self.security = SecurityUtils()
        self.verification_codes = {}
        self.verification_attempts = {}
        
    async def start_verification(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало процесса верификации"""
        query = update.callback_query
        await query.answer()
        
        keyboard = [
            [InlineKeyboardButton("📱 По номеру телефона", callback_data="verify_phone")],
            [InlineKeyboardButton("📧 По email", callback_data="verify_email")],
            [InlineKeyboardButton("📄 Загрузить документы", callback_data="verify_docs")],
            [InlineKeyboardButton("« Назад", callback_data="back_to_settings")]
        ]
        
        await query.message.edit_text(
            "🔐 Верификация пользователя\n\n"
            "Выберите способ подтверждения личности:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data['state'] = States.VERIFICATION_START
        
    async def handle_phone_verification(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка верификации по телефону"""
        query = update.callback_query
        await query.answer()
        
        keyboard = [
            [InlineKeyboardButton("📱 Отправить мой номер", callback_data="share_phone")],
            [InlineKeyboardButton("« Назад", callback_data="back_to_verification")]
        ]
        
        await query.message.edit_text(
            "📱 Верификация по номеру телефона\n\n"
            "1. Нажмите кнопку «Отправить мой номер»\n"
            "2. Вам придет SMS с кодом подтверждения\n"
            "3. Введите полученный код\n\n"
            "ℹ️ Номер телефона будет использоваться только для верификации",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data['state'] = States.VERIFICATION_PHONE
        
    async def handle_email_verification(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка верификации по email"""
        query = update.callback_query
        await query.answer()
        
        await query.message.edit_text(
            "📧 Верификация по email\n\n"
            "Отправьте ваш email адрес в чат.\n"
            "Мы отправим на него код подтверждения.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("« Назад", callback_data="back_to_verification")
            ]])
        )
        context.user_data['state'] = States.VERIFICATION_EMAIL
        
    async def handle_docs_verification(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка верификации через документы"""
        query = update.callback_query
        await query.answer()
        
        await query.message.edit_text(
            "📄 Верификация через документы\n\n"
            "Загрузите фотографию или скан документа:\n"
            "- Паспорт (первая страница)\n"
            "- Удостоверение спасателя\n"
            "- Удостоверение волонтера\n\n"
            "⚠️ Требования к файлу:\n"
            f"- Максимальный размер: {MAX_DOCUMENT_SIZE/1024/1024:.1f} МБ\n"
            "- Форматы: JPG, PNG, PDF\n"
            "- Хорошее качество изображения",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("« Назад", callback_data="back_to_verification")
            ]])
        )
        context.user_data['state'] = States.VERIFICATION_DOCS
        
    async def handle_phone_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка кода подтверждения телефона"""
        user_id = update.effective_user.id
        code = update.message.text.strip()
        
        if not self._validate_verification_attempts(user_id):
            await update.message.reply_text(
                "⚠️ Превышено количество попыток. Попробуйте позже."
            )
            return
            
        stored_code = self.verification_codes.get(user_id)
        if stored_code and stored_code == code:
            await self._complete_verification(update, context, "phone")
        else:
            await self._handle_failed_verification(update, context)
            
    async def handle_email_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка кода подтверждения email"""
        user_id = update.effective_user.id
        code = update.message.text.strip()
        
        if not self._validate_verification_attempts(user_id):
            await update.message.reply_text(
                "⚠️ Превышено количество попыток. Попробуйте позже."
            )
            return
            
        stored_code = self.verification_codes.get(user_id)
        if stored_code and stored_code == code:
            await self._complete_verification(update, context, "email")
        else:
            await self._handle_failed_verification(update, context)
            
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка загруженного документа"""
        document = update.message.document
        
        # Проверка типа файла
        if not document.mime_type in ALLOWED_DOCUMENT_TYPES:
            await update.message.reply_text(
                "❌ Неподдерживаемый формат файла.\n"
                "Допустимые форматы: JPG, PNG, PDF"
            )
            return
            
        # Проверка размера
        if document.file_size > MAX_DOCUMENT_SIZE:
            await update.message.reply_text(
                f"❌ Файл слишком большой.\n"
                f"Максимальный размер: {MAX_DOCUMENT_SIZE/1024/1024:.1f} МБ"
            )
            return
            
        # Сохраняем документ
        file = await context.bot.get_file(document.file_id)
        file_path = f"temp/docs/{update.effective_user.id}_{document.file_name}"
        await file.download_to_drive(file_path)
        
        # Отправляем на проверку администратору
        await self._send_document_for_review(update, context, file_path)
        
    async def _send_document_for_review(self, update: Update, context: ContextTypes.DEFAULT_TYPE, file_path: str):
        """Отправка документа на проверку администратору"""
        user = update.effective_user
        
        # Сохраняем информацию о документе в БД
        self.db.save_verification_document(
            user_id=user.id,
            document_path=file_path,
            status="pending"
        )
        
        # Уведомляем пользователя
        await update.message.reply_text(
            "📄 Документ успешно загружен и отправлен на проверку.\n"
            "Мы уведомим вас о результатах проверки."
        )
        
        # Логируем действие
        logger.info(f"User {user.id} uploaded document for verification: {file_path}")
        
    def _generate_verification_code(self) -> str:
        """Генерация кода подтверждения"""
        return ''.join(random.choices(string.digits, k=6))
        
    def _validate_verification_attempts(self, user_id: int) -> bool:
        """Проверка количества попыток верификации"""
        attempts = self.verification_attempts.get(user_id, {"count": 0, "last_attempt": None})
        
        # Сброс счетчика после 24 часов
        if attempts["last_attempt"] and \
           datetime.now() - attempts["last_attempt"] > timedelta(hours=24):
            attempts = {"count": 0, "last_attempt": None}
            
        # Проверка количества попыток
        if attempts["count"] >= 3:
            return False
            
        # Обновление счетчика
        attempts["count"] += 1
        attempts["last_attempt"] = datetime.now()
        self.verification_attempts[user_id] = attempts
        
        return True
        
    async def _complete_verification(self, update: Update, context: ContextTypes.DEFAULT_TYPE, method: str):
        """Завершение процесса верификации"""
        user_id = update.effective_user.id
        
        # Обновляем статус верификации в БД
        self.db.update_user_verification(
            user_id=user_id,
            verified=True,
            verification_method=method
        )
        
        # Очищаем временные данные
        self.verification_codes.pop(user_id, None)
        self.verification_attempts.pop(user_id, None)
        
        # Уведомляем пользователя
        await update.message.reply_text(
            "✅ Верификация успешно завершена!\n"
            "Теперь вам доступны все функции бота."
        )
        
        # Возвращаемся в главное меню
        context.user_data['state'] = States.MAIN_MENU
        
    async def _handle_failed_verification(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка неудачной попытки верификации"""
        attempts = self.verification_attempts.get(update.effective_user.id, {"count": 0})
        attempts_left = 3 - attempts["count"]
        
        await update.message.reply_text(
            f"❌ Неверный код. Осталось попыток: {attempts_left}"
        )