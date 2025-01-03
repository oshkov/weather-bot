import pytz
from datetime import datetime
import asyncio
from aiogram import Bot
import logging

from database import Database
from gismeteo_api import Gismeteo
from cache import Cache
import config
import keyboards
import messages


moscow_tz = pytz.timezone('Europe/Moscow') # Часовой пояс Москвы
bot = Bot(token=config.BOT_TOKEN)
database = Database(config.DATABASE_URL)
gismeteo = Gismeteo(config.GISMETEO_API_TOKEN)
cache = Cache(config.REDIS_URL)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# Словарь с временными данными {"id города":"данные о погоде"}
# Сначала данные собираются в словарь а потом в одном цикле происходит рассылка уведомлений
city_data_dict = {}


# Функция отправки уведомлений
async def send_notification(request_type):
    # Создание сессии
    try:
        async for session in database.get_session():

            # Получение данных о пользователе
            users_with_notifications = await database.get_users_with_notifications(session)

            for user in users_with_notifications:

                # Если город уже есть в списке то он не добавляется
                if user.city_id not in city_data_dict:

                    # Проверка на наличие кэша в бд
                    weather_cache = await cache.check_cache(user.city_id, request_type)

                    if weather_cache:
                        weather = weather_cache

                    else:
                        # Получение данных от гисметео
                        weather = gismeteo.get_weather(user.city_id, request_type).json()

                        # Запись в бд о запросе
                        await database.create_request(session, 'bot', user.city_id, request_type, weather)
                        
                        # Запись ответа в кэш
                        await cache.create_cache(user.city_id, request_type, weather)

                    # Добавление информации о погоде в словарь
                    city_data_dict[user.city_id] = weather

    except Exception as error:
        logging.error(f'send_notification() Session error: {error}')

    try:
        for user in users_with_notifications:

            # Получение данных о погоде из словаря
            weather = city_data_dict.get(f'{user.city_id}')

            if request_type == 'today':
                await bot.send_message(
                    chat_id=user.id,
                    text=await messages.WEATHER_TODAY(weather),
                    reply_markup=await keyboards.MENU(user.city_url, None, user.notification_status),
                    parse_mode='html'
                )

            elif request_type == 'tomorrow':
                await bot.send_message(
                    chat_id=user.id,
                    text=await messages.WEATHER_TOMORROW(weather),
                    reply_markup=await keyboards.MENU(user.city_url, 'tomorrow', user.notification_status),
                    parse_mode='html'
                )

        # Очистка временных данных
        city_data_dict.clear()

    except Exception as error:
        logging.error(f'send_notification() error: {error}')


async def main():
    logging.info('Уведомления запущены')
    while True:
        # Получаем текущее время в Москве
        moscow_time = datetime.now(moscow_tz)
        current_time_str = moscow_time.strftime('%H:%M')

        if current_time_str == '07:00':
            request_type = 'today'
            await send_notification(request_type)

        elif current_time_str == '21:00':
            request_type = 'tomorrow'
            await send_notification(request_type)
        
        # Ожидание 60 секунд перед следующей проверкой
        await asyncio.sleep(60)


# Запуск асинхронного цикла
if __name__ == "__main__":
    asyncio.run(main())
