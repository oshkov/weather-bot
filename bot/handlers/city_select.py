from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import logging

from database import Database, DatabaseError
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


@router.message(F.text == "/changecity")
@protected_route
async def request_for_city(message: Message, state: FSMContext):
    '''Запрос города'''

    try:
        # Сброс состояния при его налиции
        await state.clear()

        # Создание сессии
        async for session in database.get_session():

            # Получение данных о пользователе
            user_info = await database.get_user_information(session, message)

            # Проверка на количество запросов в этом месяце
            if await database.check_allowed_requests(session, user_info.id) == False:
                await message.answer(text=messages.ERROR_ALLOWED_REQUESTS)
                return

        await message.answer(text=messages.WRITE_CITY)

        # Создается состояние для запроса города
        await state.set_state(City.request_for_city)

    except DatabaseError as error:
        logging.error(f'request_for_city() error: {error}')
        await message.answer(await messages.DATABASE_ERROR(error))
        return

    except Exception as error:
        logging.error(f'request_for_city() error: {error}')
        await message.answer(await messages.DATABASE_ERROR(error))
        return


@router.message(City.request_for_city)
@protected_route
async def search_city_handler(message: Message, state: FSMContext):
    '''Поиск городов'''

    try:
        # Сброс состояния при его налиции
        await state.clear()

        loading_message = await message.answer(messages.LOADING)

        city_name = message.text
        request_type = 'cities'

        # Создание сессии
        async for session in database.get_session():

            # Проверка на наличие кэша в бд
            city_cache = await cache.check_cache(city_name, request_type)

            if city_cache:
                cities_dict = city_cache

            else:
                # Получение данных от гисметео
                cities_dict = gismeteo.get_cities(city_name).json()

                # Запись в бд о запросе
                await database.create_request(session, message.from_user.id, city_name, request_type)

                # Запись ответа в кэш
                await cache.create_cache(city_name, request_type, cities_dict)

        if len(cities_dict['response']['items']) != 0:
            await loading_message.edit_text(
                text=messages.SELECT_CITY,
                reply_markup=await keyboards.SELECT_CITY(cities_dict)
            )

            # Передача списка городов в состояние
            cities_dict = {'cities_dict': cities_dict}
            await state.update_data(cities_dict=cities_dict)

        else:
            await loading_message.edit_text(text=messages.SELECT_CITY_ERROR)

    except DatabaseError as error:
        logging.error(f'search_city_handler() error: {error}')
        await loading_message.delete()
        await message.answer(await messages.DATABASE_ERROR(error))
        return

    except Exception as error:
        logging.error(f'search_city_handler() error: {error}')
        await loading_message.delete()
        await message.answer(await messages.ERROR(error))
        return


@router.callback_query(F.data.contains('add_city'))
@protected_route
async def add_city_handler(callback: CallbackQuery, state: FSMContext):
    '''Выбор города'''

    try:
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
        async for session in database.get_session():

            # Добавление города к пользователю в бд
            await database.add_city(session, callback, city_id, city_name, city_url)
            
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

        await callback.answer(messages.SUCCESS_CITY_CONNECTED)

        await weather.weather_callback_handler(callback, state)

    except DatabaseError as error:
        logging.error(f'add_city_handler() error: {error}')
        await callback.message.answer(await messages.DATABASE_ERROR(error))
        return

    except Exception as error:
        logging.error(f'add_city_handler() error: {error}')
        await callback.message.answer(await messages.ERROR(error))
        return