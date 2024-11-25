from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

from database import Database
from cache import Cache
from utils import protected_route
import config
import messages
import keyboards
import handlers.city_select as city_select


router = Router()
database = Database(config.DATABASE_URL)
cache = Cache(config.REDIS_URL)


# Команда /start
@router.message(F.text.contains("/start"))
@protected_route
async def start_handler(message: Message, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Создание сессии
    try:
        async for session in database.get_session():

            # Добавление пользователя в бд
            if await database.add_user(session, message) == False:
                await message.answer(
                    text=messages.ERROR_START,
                    show_alert=True
                )
                return
            
    except Exception as error:
        logging.error(f'start_handler() Session error: {error}')
        await message.answer(await messages.DATABASE_ERROR(error))
        return

    try:
        # Запрос города
        await city_select.request_for_city(message, state)

    except Exception as error:
        logging.error(f'start_handler() error: {error}')


# Команда /about
@router.message(F.text.contains("/about"))
@protected_route
async def about_command_handler(message: Message, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()
    
    await message.answer(
        text=messages.ABOUT,
        parse_mode='html'
    )


# Переключение уведомлений
@router.callback_query(F.data.contains('notification_switch'))
@protected_route
async def notification_switch_handler(callback: CallbackQuery, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    request_type = None
    if len(callback.data.split()) > 1:
        request_type = callback.data.split()[1]

    # Создание сессии
    try:
        async for session in database.get_session():

            # Получение данных о пользователе
            user_info = await database.get_user_information(session, callback)
            city_url = user_info.city_url

            # Вкл/Выкл уведомления
            if user_info.notification_status == 0:
                new_notification_status = 1
                user_info.notification_status = new_notification_status

            elif user_info.notification_status == 1:
                new_notification_status = 0
                user_info.notification_status = new_notification_status

            # Сохранение данных в бд
            await session.commit()

    except Exception as error:
        logging.error(f'notification_switch_handler() Session error: {error}')
        await callback.message.answer(await messages.DATABASE_ERROR(error))
        return

    try:
        if new_notification_status == 1:
            await callback.answer(
                text=messages.NOTIFICATION_ON,
                show_alert=True
            )

        elif new_notification_status == 0:
            await callback.answer(
                text=messages.NOTIFICATION_OFF,
                show_alert=True
            )

        await callback.message.edit_reply_markup(
            inline_message_id=callback.inline_message_id,
            reply_markup=await keyboards.MENU(city_url, request_type, new_notification_status)
        )

    except Exception as error:
        logging.error(f'notification_switch_handler() error: {error}')
        await callback.message.answer(await messages.ERROR(error))
        return


# Команда /stats
@router.message(F.text.contains("/stats"))
@protected_route
async def stats_command_handler(message: Message, state: FSMContext):
    # Сброс состояния при его налиции
    await state.clear()

    # Создание сессии
    try:
        async for session in database.get_session():

            # Получение всех запросов за месяц
            month_requests = await database.get_month_requests(session)

            # Получение всех пользователей
            users = await database.get_all_users(session)

    except Exception as error:
        logging.error(f'stats_command_handler() Session error: {error}')
        await message.answer(await messages.DATABASE_ERROR(error))
        return

    try:
        redis_connect = await cache.check_connect()
        db_connect = await database.check_connect()

        await message.answer(
            text=await messages.STATS(month_requests, users, redis_connect, db_connect),
            parse_mode='html'
        )

    except Exception as error:
        logging.error(f'stats_command_handler() error: {error}')
        await message.answer(await messages.ERROR(error))
        return