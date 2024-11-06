from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

from database import Database
from gismeteo_api import Gismeteo
from cache import Cache
import config
import keyboards
import messages


router = Router()
database = Database(config.DATABASE_URL)
gismeteo = Gismeteo(config.GISMETEO_API_TOKEN)
cache = Cache(config.REDIS_URL)


# Вывод погоды при нажатии на клавиатуре
@router.callback_query(F.data.contains('weather'))
async def weather_callback_handler(callback: CallbackQuery, state: FSMContext, from_city_select: bool = False):
    # Сброс состояния при его налиции
    await state.clear()

    # Проверка на доступ к боту
    if str(callback.from_user.id) not in config.USERS:
        return

    # Сообщение загрузки
    await callback.message.edit_text(
        text=messages.LOADING,
        inline_message_id=callback.inline_message_id,
        reply_markup=callback.message.reply_markup
    )

    # Получение типа запроса
    if from_city_select == True:
        request_type = 'now'
    else:
        request_type = callback.data.split()[1]

    # Создание сессии
    try:
        async for session in database.get_session():

            # Получение данных о пользователе
            user_info = await database.get_user_information(session, callback)

            city_id = user_info.city_id
            city_url = user_info.city_url
            notification_status = user_info.notification_status

            # Проверка на наличие кэша в бд
            weather_cache = await cache.check_cache(city_id, request_type)

            if weather_cache:
                weather = weather_cache

            else:
                # Проверка на количество запросов в этом месяце
                if await database.check_allowed_requests(session, user_info.id):

                    # Получение данных от гисметео
                    weather = gismeteo.get_weather(city_id, request_type).json()

                    # Запись в бд о запросе
                    await database.create_request(session, callback.from_user.id, city_id, request_type, weather)

                    # Запись ответа в кэш
                    await cache.create_cache(city_id, request_type, weather)

                else:
                    await callback.answer(
                        text=messages.ERROR_ALLOWED_REQUESTS,
                        show_alert=True
                    )
                    await callback.message.edit_text(
                        text=callback.message.text,
                        inline_message_id=callback.inline_message_id,
                        reply_markup=callback.message.reply_markup
                    )
                    return

    except Exception as error:
        logging.error(f'weather_callback_handler() Session error: {error}')
        await callback.message.answer(await messages.DATABASE_ERROR(error))
        return

    # Вывод ответа
    try:
        if request_type == 'now':
            await callback.message.edit_text(
                text=await messages.WEATHER_NOW(weather),
                reply_markup=await keyboards.MENU(city_url, request_type, notification_status),
                parse_mode='html'
            )

        elif request_type == 'today':
            await callback.message.edit_text(
                text=await messages.WEATHER_TODAY(weather),
                reply_markup=await keyboards.MENU(city_url, None, notification_status),
                parse_mode='html'
            )

        elif request_type == 'tomorrow':
            await callback.message.edit_text(
                text=await messages.WEATHER_TOMORROW(weather),
                reply_markup=await keyboards.MENU(city_url, request_type, notification_status),
                parse_mode='html'
            )

        elif request_type == '10-days':
            await callback.message.edit_text(
                text=await messages.WEATHER_10_DAYS(weather),
                reply_markup=await keyboards.MENU(city_url, request_type, notification_status),
                parse_mode='html'
            )

    except Exception as error:
        logging.error(f'weather_callback_handler() error: {error}')
        await callback.message.answer(await messages.ERROR(error))
        return


# Вывод погоды при вводе команды
@router.message(F.text == "/weather")
async def weather_command_handler(message: Message, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Проверка на доступ к боту
    if str(message.from_user.id) not in config.USERS:
        return
    
    loading_message = await message.answer(messages.LOADING)

    # Тип запроса
    request_type = 'now'
    
    # Создание сессии
    try:
        async for session in database.get_session():

            # Получение данных о пользователе
            user_info = await database.get_user_information(session, message)
            city_id = user_info.city_id
            city_url = user_info.city_url
            notification_status = user_info.notification_status

            # Проверка на наличие кэша в бд
            weather_cache = await cache.check_cache(city_id, request_type)

            if weather_cache:
                weather = weather_cache

            else:
                # Проверка на количество запросов в этом месяце
                if await database.check_allowed_requests(session, user_info.id):

                    # Получение данных от гисметео
                    weather = gismeteo.get_weather(city_id, request_type).json()

                    # Запись в бд о запросе
                    await database.create_request(session, message.from_user.id, city_id, request_type, weather)

                    # Запись запроса в кэш
                    await cache.create_cache(city_id, request_type, weather)

                else:
                    await loading_message.edit_text(text=messages.ERROR_ALLOWED_REQUESTS)
                    return

    except Exception as error:
        logging.error(f'weather_command_handler() Session error: {error}')
        await loading_message.delete()
        await message.answer(await messages.DATABASE_ERROR(error))
        return

    try:
        await loading_message.edit_text(
            text=await messages.WEATHER_NOW(weather),
            reply_markup=await keyboards.MENU(city_url, request_type, notification_status),
            parse_mode='html'
        )

    except Exception as error:
        logging.error(f'weather_command_handler() error: {error}')
        await message.answer(await messages.ERROR(error))
        return