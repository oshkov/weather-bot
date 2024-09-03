import asyncio
from aiogram import Bot, Dispatcher

import config
import handlers.city_select as city_select
import handlers.main as main
import handlers.weather as weather


bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
dp.include_routers(
    city_select.router,
    main.router,
    weather.router
)


# Запуск бота
async def start_bot():
    print('Бот запущен')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(start_bot())