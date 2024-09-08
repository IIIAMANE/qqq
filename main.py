# .venv\Scripts\activate
# black . для всего
# git add .
# git commit -m "test"
# git push
# git pull origin main получить изменения с гита
# git rm --cached .env удалить какой то файл

import os
import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from app.handlers import router
from app.database.models import async_main


async def main():
    load_dotenv()
    await async_main()
    token = os.getenv("TOKEN")
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
