import asyncio
from aiogram import Bot, Dispatcher
import logging

import config
import handlers.city_select as city_select
import handlers.main as main
import handlers.weather as weather
from database import Database


bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
dp.include_routers(
    city_select.router,
    main.router,
    weather.router
)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)



# Запуск бота
async def start_bot():

    db = Database(config.DATABASE_URL)
    await db.init_tables()
    logging.info('Таблицы в бд созданы')

    logging.info('Бот запущен')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(start_bot())