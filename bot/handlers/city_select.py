from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import logging

from database import Database
from gismeteo_api import Gismeteo
from cache import Cache
from utils import protected_route
import config
import keyboards
import messages
import handlers.weather as weather


router = Router()
gismeteo = Gismeteo(config.GISMETEO_API_TOKEN)
database = Database(config.DATABASE_URL)
cache = Cache(config.REDIS_URL)


class City(StatesGroup):
    request_for_city = State()


# Запрос города
@router.message(F.text == "/changecity")
@protected_route
async def request_for_city(message: Message, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Проверка на доступ к боту
    if str(message.from_user.id) not in config.USERS:
        return
    
    # Создание сессии
    try:
        async for session in database.get_session():

            # Получение данных о пользователе
            user_info = await database.get_user_information(session, message)

            # Проверка на количество запросов в этом месяце
            if await database.check_allowed_requests(session, user_info.id) == False:
                await message.answer(text=messages.ERROR_ALLOWED_REQUESTS)
                return

    except Exception as error:
        logging.error(f'request_for_city() Session error: {error}')
        await message.answer(await messages.DATABASE_ERROR(error))
        return

    await message.answer(text=messages.WRITE_CITY)

    # Создается состояние для запроса города
    await state.set_state(City.request_for_city)


# Поиск городов
@router.message(City.request_for_city)
@protected_route
async def search_city_handler(message: Message, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Проверка на доступ к боту
    if str(message.from_user.id) not in config.USERS:
        return

    city_name = message.text
    request_type = 'cities'

    # Создание сессии
    try:
        async for session in database.get_session():

            # Проверка на наличие кэша в бд
            city_cache = await cache.check_cache(city_name, request_type)

            if city_cache:
                cities_dict = city_cache

            else:
                # Получение данных от гисметео
                cities_dict = gismeteo.get_cities(city_name).json()

                # Запись в бд о запросе
                await database.create_request(session, message.from_user.id, city_name, request_type, cities_dict)

                # Запись ответа в кэш
                await cache.create_cache(city_name, request_type, cities_dict)

    except Exception as error:
        logging.error(f'search_city_handler() Session error: {error}')
        await message.answer(await messages.DATABASE_ERROR(error))
        return

    try:
        if len(cities_dict['response']['items']) != 0:
            await message.answer(
                text=messages.SELECT_CITY,
                reply_markup=await keyboards.SELECT_CITY(cities_dict)
            )

            # Передача списка городов в состояние
            cities_dict = {'cities_dict': cities_dict}
            await state.update_data(cities_dict=cities_dict)

        else:
            await message.answer(text=messages.SELECT_CITY_ERROR)

    except Exception as error:
        logging.error(f'search_city_handler() error: {error}')
        await message.answer(await messages.ERROR(error))
        return


# Выбор города
@router.callback_query(F.data.contains('add_city'))
@protected_route
async def add_city_handler(callback: CallbackQuery, state: FSMContext):
    # Проверка на доступ к боту
    if str(callback.from_user.id) not in config.USERS:
        return

    # Получение списка городов
    data = await state.get_data()
    cities_dict = data['cities_dict']['cities_dict']['response']['items']

    # Выбранный город
    city_id = callback.data.split()[1]

    for city in cities_dict:
        if str(city['id']) == city_id:
            city_name = city['name']
            city_url = city['url']
            break

    # Сброс состояния
    await state.clear()

    # Создание сессии
    try:
        async for session in database.get_session():

            # Добавление города к пользователю в бд
            if await database.add_city(session, callback, city_id, city_name, city_url) == False:
                await callback.answer(
                    text=messages.ERROR_CITY_CONNECTED,
                    show_alert=True
                )
                return
            
            # Проверка на количество запросов в этом месяце
            if await database.check_allowed_requests(session, callback.from_user.id) == False:
                await callback.answer(
                    text=messages.ERROR_ALLOWED_REQUESTS,
                    show_alert=True
                )
                await callback.message.edit_text(
                    text=messages.SUCCESS_CITY_CONNECTED,
                    reply_markup=None
                )
                return

    except Exception as error:
        logging.error(f'add_city_handler() Session error: {error}')
        await callback.message.answer(await messages.DATABASE_ERROR(error))
        return

    try:
        await callback.answer(messages.SUCCESS_CITY_CONNECTED)

        # await weather.weather_callback_handler(callback, state, from_city_select=True)
        await weather.weather_callback_handler(callback, state)

    except Exception as error:
        logging.error(f'add_city_handler() error: {error}')
        await callback.message.answer(await messages.ERROR(error))
        return