import asyncio
from aiogram import Dispatcher
from services import check_new_posts, bot
from handlers import setup_handlers

dp = Dispatcher()

setup_handlers(dp)

async def main():
    asyncio.create_task(check_new_posts())
    await dp.start_polling(bot)
    await task

if __name__ == "__main__":
    asyncio.run(main())