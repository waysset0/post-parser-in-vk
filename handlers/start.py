from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот для отслеживания новых постов ВКонтакте.\n\n"
        "📌 Добавить подписку можно:\n"
        "1. По ссылке: /add https://vk.com/durov\n"
        "2. По короткому имени: /add durov\n"
        "3. По ID: /add id1 или /add club1\n\n"
        "📋 Посмотреть свои подписки: /list\n"
        "❌ Удалить подписку: /remove"
    )