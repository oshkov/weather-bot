from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from database import Database
from gismeteo_api import Gismeteo
import config
import keyboards
import messages
import handlers.weather as weather


router = Router()
gismeteo = Gismeteo(config.GISMETEO_API_TOKEN)
database = Database(config.DATABASE_URL)


class City(StatesGroup):
    request_for_city = State()


# Запрос города
@router.message(F.text == "/changecity")
async def request_for_city(message: Message, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Проверка на доступ к боту
    if str(message.from_user.id) not in config.USERS:
        return

    await message.answer(text=messages.WRITE_CITY)

    # Создается состояние для запроса города
    await state.set_state(City.request_for_city)


# Поиск городов
@router.message(City.request_for_city)
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

            city_cache = await database.check_cache(session, city_name, request_type)
            if city_cache:
                cities_dict = city_cache
            else:
                cities_dict = gismeteo.get_cities(city_name).json()
                await database.create_cache(session, message.from_user.id, city_name, request_type, cities_dict)

    except Exception as error:
        print(f'search_city_handler() Session error: {error}')

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
        print(f'search_city_handler() error: {error}')


# Выбор города
@router.callback_query(F.data.contains('add_city'))
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

    except Exception as error:
        print(f'add_city_handler() Session error: {error}')

    try:
        await callback.answer(messages.SUCCESS_CITY_CONNECTED)

        await weather.weather_callback_handler(callback, state, from_city_select=True)

    except Exception as error:
        print(f'add_city_handler() error: {error}')