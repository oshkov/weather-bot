from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo


# Выбор города
async def MENU(city_url, request_type, notification_status):

    # Проверка на статус уведомлений
    if notification_status == 1:
        notification_status = '🔕 Выкл.'
    elif notification_status == 0:
        notification_status = '🔔 Вкл.'

    # Если запрос погоды на сегодня
    if request_type == None:
        request_type = ''

    markup = [
        [
            InlineKeyboardButton(text='Сейчас', callback_data=f'weather now'),
            InlineKeyboardButton(text='Сегодня', callback_data=f'weather today')
        ],
        [
            InlineKeyboardButton(text='10 дней', callback_data=f'weather 10-days'),
            InlineKeyboardButton(text='Завтра', callback_data=f'weather tomorrow')
        ],
        [
            InlineKeyboardButton(text=f'{notification_status} уведомления', callback_data=f'notification_switch {request_type}')
        ],
        # [
        #     InlineKeyboardButton(text='🌍 Подробнее на Gismeteo', web_app=WebAppInfo(url=f'https://www.gismeteo.ru{city_url}{request_type}'))
        # ],
        [
            InlineKeyboardButton(text='🌍 Подробнее на Gismeteo', url=f'https://www.gismeteo.ru{city_url}{request_type}')
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard= markup)
    return keyboard