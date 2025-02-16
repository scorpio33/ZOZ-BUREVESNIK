import pytest
from unittest.mock import AsyncMock, MagicMock
from telegram import Update, Message, User, Chat
from telegram.ext import Application
from core.bot import Bot, States

@pytest.fixture
def bot():
    app = MagicMock(spec=Application)
    return Bot(app)

@pytest.fixture
def update():
    update = MagicMock(spec=Update)
    update.effective_user = MagicMock(spec=User)
    update.effective_user.id = 123456789
    update.message = MagicMock(spec=Message)
    update.message.chat = MagicMock(spec=Chat)
    return update

@pytest.fixture
def context():
    context = MagicMock()
    context.user_data = {}
    return context

@pytest.mark.asyncio
async def test_start_command(bot, update, context):
    result = await bot.start_command(update, context)
    assert result == States.START
    update.message.reply_text.assert_called_once()

@pytest.mark.asyncio
async def test_auth_success(bot, update, context):
    update.message.text = 'KREML'
    result = await bot.handle_auth(update, context)
    assert result == States.MAIN_MENU
    assert context.user_data['authorized'] is True

@pytest.mark.asyncio
async def test_auth_failure(bot, update, context):
    update.message.text = 'wrong_password'
    result = await bot.handle_auth(update, context)
    assert result == States.AUTH
    assert 'authorized' not in context.user_data