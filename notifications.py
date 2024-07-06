import pytz
from datetime import datetime
import asyncio
from aiogram import Bot

from database import Database
from gismeteo_api import Gismeteo
import config
import keyboards
import messages


moscow_tz = pytz.timezone('Europe/Moscow') # Часовой пояс Москвы
bot = Bot(token=config.BOT_TOKEN)
database = Database(config.DATABASE_URL)
gismeteo = Gismeteo(config.GISMETEO_API_TOKEN)


# Словарь с временными данными ("id города":"погода")
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
                    weather_cache = await database.check_cache(session, user.city_id, request_type)
                    if weather_cache:
                        weather = weather_cache
                    else:
                        weather = gismeteo.get_weather(user.city_id, request_type).json()
                        await database.create_cache(session, 'by-bot', user.city_id, request_type, weather)

                    # Добавление информации о погоде в словарь
                    city_data_dict[user.city_id] = weather

    except Exception as error:
        print(f'send_notification() Session error: {error}')

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
                    reply_markup=await keyboards.MENU(user.city_url, None, user.notification_status),
                    parse_mode='html'
                )

        city_data_dict.clear()
        print(city_data_dict)


    except Exception as error:
        print(f'send_notification() error: {error}')


async def main():
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
