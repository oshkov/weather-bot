from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo


# Выбор города
async def SELECT_CITY(cities_list):
    markup = []
    for city in cities_list['response']['items']:
        button_text = ''
        if city['name']:
            button_text += city['name']

        if city['district']:
            button_text += f", {city['district']['name']}"

        if city['country']['name']:
            button_text += f", {city['country']['name']}"

        if city['kind'] == 'A':
            button_text = f'✈️ {button_text}'

        country_code = city['country']['code']
        flag = chr(ord(country_code[0]) + 0x1F1E6 - ord('A')) + chr(ord(country_code[1]) + 0x1F1E6 - ord('A'))
        button_text = f'{flag} {button_text}'

        markup.append([InlineKeyboardButton(text=button_text, callback_data= f"add_city {city['id']}")])

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