from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo


# Выбор города
async def SELECT_CITY(cities_list):
    markup = []
    for city in cities_list['response']['items']:
        markup.append([InlineKeyboardButton(text= f"{city['name']}, {city['district']['name']}", callback_data= f"add_city {city['id']}")])

    keyboard = InlineKeyboardMarkup(inline_keyboard= markup)
    return keyboard


# Выбор города
async def MENU(city_url, request_type, notification_status):

    if notification_status == 1:
        notification_status = 'Выкл.'
    elif notification_status == 0:
        notification_status = 'Вкл.'

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
        #     InlineKeyboardButton(text='Подробнее на Gismeteo', web_app=WebAppInfo(url=f'https://www.gismeteo.ru{city_url}{"" if request_type is None else request_type}'))
        # ],
        [
            InlineKeyboardButton(text='Подробнее на Gismeteo', url=f'https://www.gismeteo.ru{city_url}{"" if request_type is None else request_type}')
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard= markup)
    return keyboard