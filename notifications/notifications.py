import pytz
from datetime import datetime
import asyncio
from aiogram import Bot
import logging

from database import Database, DatabaseError
from gismeteo_api import Gismeteo
from cache import Cache
import config
import keyboards
import messages


bot = Bot(token=config.BOT_TOKEN)
database = Database(config.DATABASE_URL)
gismeteo = Gismeteo(config.GISMETEO_API_TOKEN)
cache = Cache(config.REDIS_URL)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

city_data_dict = {}    # Словарь с временными данными {"id города": данные_о_погоде}


async def send_notification(request_type):
    '''
    Отправка уведомлений
    
    Сначала происходит сбор погоды на все города, а потом рассылка
    '''

    try:
        # Создание сессии
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
                        await database.create_request(session, 'bot', user.city_id, request_type)
                        
                        # Запись ответа в кэш
                        await cache.create_cache(user.city_id, request_type, weather)

                    # Добавление информации о погоде в словарь
                    city_data_dict[user.city_id] = weather

        # Рассылка уведомлений
        for user in users_with_notifications:
            # Получение данных о погоде из словаря
            weather = city_data_dict.get(f'{user.city_id}')

            if request_type == 'today':
                text = await messages.WEATHER_TODAY(weather)
                markup = await keyboards.MENU(user.city_url, None, user.notification_status)

            elif request_type == 'tomorrow':
                text = await messages.WEATHER_TOMORROW(weather)
                markup = await keyboards.MENU(user.city_url, 'tomorrow', user.notification_status)

            try:
                await bot.send_message(
                    chat_id=user.id,
                    text=text,
                    reply_markup=markup,
                    parse_mode='html'
                )

            except Exception as error:
                logging.error(f'{config.USERS.get(str(user.id))} не получил(а) уведомление! Ошибка: {error}')

        # Очистка временных данных
        city_data_dict.clear()

    except DatabaseError as error:
        logging.error(f'send_notification() database error: {error}')

    except Exception as error:
        logging.error(f'send_notification() error: {error}')


async def main():
    '''Функция для проверки времени и запуска уведомлений'''

    logging.info('Уведомления запущены')

    while True:
        moscow_time = datetime.now(pytz.timezone('Europe/Moscow'))    # Текущее время в Москве
        current_time_str = moscow_time.strftime('%H:%M')

        if current_time_str == '07:00':
            await send_notification('today')

        elif current_time_str == '21:00':
            await send_notification('tomorrow')
        
        await asyncio.sleep(60)    # Пауза на 60 секунд перед следующей проверкой


if __name__ == "__main__":
    asyncio.run(main())
