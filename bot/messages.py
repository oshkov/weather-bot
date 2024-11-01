import datetime
import config


weekdays = ['Пн','Вт','Ср','Чт','Пт','Сб','Вс']
months = ['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря']


ERROR_START = 'Произошла ошибка, попробуйте ещё раз'
ERROR_ALLOWED_REQUESTS = '🤯 Вы сделали слишком много запросов в этом месяце\n\nДо конца месяца вы сможете получать только уведомления от бота'
WRITE_CITY = 'Напиши название города, в котором хочешь узнать погоду'
SELECT_CITY = 'Выбери город из предложенных'
SELECT_CITY_ERROR = 'Произошла ошибка: город не найден\nВведи название города заново'
SUCCESS_CITY_CONNECTED = '✅ Город успешно привязан к вашему аккаунту'
ERROR_CITY_CONNECTED = 'Произошла ошибка, не удалось привязать город к вашему аккаунту'
ABOUT = 'Этот приватный бот создан по личной инициативе @oshkov\n\nБот использует официальное API от <a href="https://www.gismeteo.ru/">Gismeteo</a>'
NOTIFICATION_ON = 'Уведомления включены🔔\n\nВы будете получать уведомления в 7.00 и 21.00 по мск каждый день'
NOTIFICATION_OFF = 'Уведомления выключены🔕'
LOADING = 'Загрузка данных...'


def get_date(data, index_data: int):
    date = data[index_data]['date']['local']
    date_obj = datetime.datetime.strptime(str(date), "%Y-%m-%dT%H:%M:%SZ")
    weekday = weekdays[date_obj.weekday()]
    day = date_obj.day
    month = months[date_obj.month - 1]
    date_today_formatted = f'{weekday}, {day} {month}'

    return date_today_formatted

def get_sunrise_time(data, index_data: int):
    # Обработка восхода, захода солнца и проверка полярного дня/ночи
    sunrise_date = datetime.datetime.fromisoformat(data[index_data]['astro']['sun']['sunrise'])
    date_today = datetime.datetime.now().date()

    sunrise_hours = sunrise_date.hour
    sunrise_minutes = sunrise_date.minute
    if sunrise_minutes < 10:
        sunrise_minutes = f'0{sunrise_minutes}'
    sunrise_time = f'{sunrise_hours}:{sunrise_minutes}'
    if sunrise_date.date() != date_today:
        month = months[sunrise_date.month - 1]
        day = sunrise_date.day
        sunrise_time = f'{day} {month}, {sunrise_hours}:{sunrise_minutes}'

    return sunrise_time

def get_sunset_time(data, index_data: int):
    sunset_date = datetime.datetime.fromisoformat(data[index_data]['astro']['sun']['sunset'])
    date_today = datetime.datetime.now().date()

    sunset_hours = sunset_date.hour
    sunset_minutes = sunset_date.minute
    if sunset_minutes < 10:
        sunset_minutes = f'0{sunset_minutes}'
    sunset_time = f'{sunset_hours}:{sunset_minutes}'
    if sunset_date.date() != date_today:
        month = months[sunset_date.month - 1]
        day = sunset_date.day
        sunset_time = f'{day} {month}, {sunset_hours}:{sunset_minutes}'

    return sunset_time

def get_polar(data, index_data: int):
    polar = data[index_data]['astro']['sun']['polar']
    polar_text = ''
    if polar == 'day':
        polar_text = '<b>Полярный день ☀️</b>\n'
    elif polar == 'night':
        polar_text = '<b>Полярная ночь 🌙</b>\n'

    return polar_text


async def WEATHER_NOW(weather):
    # Данные о погоде
    data = weather['data']

    # Получение данных
    name_p = data['city']['nameP']
    emoji = data['icon']['emoji']
    description = data['description']
    wind_speed = round(data['wind']['speed']['m_s'])

    # Обработка температуры
    temperature = round(data['temperature']['air']['C'])
    if temperature > 0:
        temperature = f"+{temperature}"

    # Обработка температуры по ощущениям
    temperature_comfort = round(data['temperature']['comfort']['C'])
    if temperature_comfort > 0:
        temperature_comfort = f"+{temperature_comfort}"

    return f'Погода {name_p} сейчас:\n\n<b>{emoji} {description}, {temperature}°, {wind_speed} м/с</b>\n\nПо ощущениям {temperature_comfort}'


async def WEATHER_TODAY(weather):
    # Данные о погоде
    data = weather['data']

    # Название города в предложном падеже
    name_p = data[0]['city']['nameP']

    # Обработка даты сегодня в формат: Вт, 5 марта
    date = get_date(data, 0)

    # Обработка восхода, захода солнца и проверка полярного дня/ночи
    sunrise_time = get_sunrise_time(data, 0)
    sunset_time = get_sunset_time(data, 0)
    polar_text = get_polar(data, 0)

    indexes = [2,3,4,5,6,7]
    times = []
    emojis = []
    temperatures = []
    descriptions = []
    wind_speeds = []

    for index in indexes:
        # Обработка времени суток
        time = data[index]['date']['local'][11:16].replace(":", ".")
        times.append(time)

        # Получение эмодзи
        emoji = data[index]['icon']['emoji']
        emojis.append(emoji)

        # Обработка температур
        temperature = round(data[index]['temperature']['air']['C'])
        temperatures.append(temperature)

        # Получение описаний погоды
        description = data[index]['description']
        descriptions.append(description)

        # Обработка ветра
        wind_speed = round(data[index]['wind']['speed']['m_s'])
        wind_speeds.append(wind_speed)

    return f'Погода {name_p} сегодня ({date}):\n\n<b>{times[0]}:</b> {emojis[0]} {temperatures[0]}°, {descriptions[0]}, {wind_speeds[0]} м/с\n<b>{times[1]}:</b> {emojis[1]} {temperatures[1]}°, {descriptions[1]}, {wind_speeds[1]} м/с\n<b>{times[2]}:</b> {emojis[2]} {temperatures[2]}°, {descriptions[2]}, {wind_speeds[2]} м/с\n<b>{times[3]}:</b> {emojis[3]} {temperatures[3]}°, {descriptions[3]}, {wind_speeds[3]} м/с\n<b>{times[4]}:</b> {emojis[4]} {temperatures[4]}°, {descriptions[4]}, {wind_speeds[4]} м/с\n<b>{times[5]}:</b> {emojis[5]} {temperatures[5]}°, {descriptions[5]}, {wind_speeds[5]} м/с\n\n{polar_text}<b>Восход:</b> {sunrise_time}\n<b>Заход:</b> {sunset_time}'


async def WEATHER_TOMORROW(weather):
    # Данные о погоде
    data = weather['data']

    # Название города в предложном падеже
    name_p = data[0]['city']['nameP']

    # Обработка даты сегодня в формат: Вт, 5 марта
    date = get_date(data, 9)

    # Обработка восхода, захода солнца и проверка полярного дня/ночи
    sunrise_time = get_sunrise_time(data, 9)
    sunset_time = get_sunset_time(data, 9)
    polar_text = get_polar(data, 9)

    indexes = [10,11,12,13,14,15]
    times = []
    emojis = []
    temperatures = []
    descriptions = []
    wind_speeds = []

    for index in indexes:
        # Обработка времени суток
        time = data[index]['date']['local'][11:16].replace(":", ".")
        times.append(time)

        # Получение эмодзи
        emoji = data[index]['icon']['emoji']
        emojis.append(emoji)

        # Обработка температур
        temperature = round(data[index]['temperature']['air']['C'])
        temperatures.append(temperature)

        # Получение описаний погоды
        description = data[index]['description']
        descriptions.append(description)

        # Обработка ветра
        wind_speed = round(data[index]['wind']['speed']['m_s'])
        wind_speeds.append(wind_speed)

    return f'Погода {name_p} завтра ({date}):\n\n<b>{times[0]}:</b> {emojis[0]} {temperatures[0]}°, {descriptions[0]}, {wind_speeds[0]} м/с\n<b>{times[1]}:</b> {emojis[1]} {temperatures[1]}°, {descriptions[1]}, {wind_speeds[1]} м/с\n<b>{times[2]}:</b> {emojis[2]} {temperatures[2]}°, {descriptions[2]}, {wind_speeds[2]} м/с\n<b>{times[3]}:</b> {emojis[3]} {temperatures[3]}°, {descriptions[3]}, {wind_speeds[3]} м/с\n<b>{times[4]}:</b> {emojis[4]} {temperatures[4]}°, {descriptions[4]}, {wind_speeds[4]} м/с\n<b>{times[5]}:</b> {emojis[5]} {temperatures[5]}°, {descriptions[5]}, {wind_speeds[5]} м/с\n\n{polar_text}<b>Восход:</b> {sunrise_time}\n<b>Заход:</b> {sunset_time}'


async def WEATHER_10_DAYS(weather):
    # Данные о погоде
    data = weather['data']

    # Название города в предложном падеже
    name_p = data[0]['city']['nameP']

    indexes = [5,13,21,29,37,45,53,61,69,77]
    dates = []
    emojis = []
    temperatures = []
    descriptions = []
    wind_speeds = []

    for index in indexes:
        # Обработка даты сегодня в формат: Вт, 5 марта
        date = get_date(data, index)
        dates.append(date)

        # Получение эмодзи
        emoji = data[index]['icon']['emoji']
        emojis.append(emoji)

        # Обработка температур
        temperature = round(data[index]['temperature']['air']['C'])
        temperatures.append(temperature)

        # Получение описаний погоды
        description = data[index]['description']
        descriptions.append(description)

        # Обработка ветра
        wind_speed = round(data[index]['wind']['speed']['m_s'])
        wind_speeds.append(wind_speed)

    return f'Погода {name_p} на 10 дней:\n\n<b>{dates[0]}:</b> {emojis[0]} {temperatures[0]}°, {descriptions[0]}, {wind_speeds[0]} м/с\n<b>{dates[1]}:</b> {emojis[1]} {temperatures[1]}°, {descriptions[1]}, {wind_speeds[1]} м/с\n<b>{dates[2]}:</b> {emojis[2]} {temperatures[2]}°, {descriptions[2]}, {wind_speeds[2]} м/с\n<b>{dates[3]}:</b> {emojis[3]} {temperatures[3]}°, {descriptions[3]}, {wind_speeds[3]} м/с\n<b>{dates[4]}:</b> {emojis[4]} {temperatures[4]}°, {descriptions[4]}, {wind_speeds[4]} м/с\n<b>{dates[5]}:</b> {emojis[5]} {temperatures[5]}°, {descriptions[5]}, {wind_speeds[5]} м/с\n<b>{dates[6]}:</b> {emojis[6]} {temperatures[6]}°, {descriptions[6]}, {wind_speeds[6]} м/с\n<b>{dates[7]}:</b> {emojis[7]} {temperatures[7]}°, {descriptions[7]}, {wind_speeds[7]} м/с\n<b>{dates[8]}:</b> {emojis[8]} {temperatures[8]}°, {descriptions[8]}, {wind_speeds[8]} м/с\n<b>{dates[9]}:</b> {emojis[9]} {temperatures[9]}°, {descriptions[9]}, {wind_speeds[9]} м/с'


async def STATS(month_requests, users, redis_connect, db_connect):
    # Создается словарь с пользователями
    user_requests_info = {
        'bot': {
            'name': 'Уведомления',
            'allowed_requests': None,
            'used_requests': 0
            }
        }

    # Добавление в словарь всех пользователей
    for user in users:
        if user.id not in user_requests_info:
            user_requests_info[user.id] = {'name': config.USERS[user.id], 'allowed_requests': user.allowed_requests, 'used_requests': 0}

    # Подсчет использованных запросов
    requests_amount = 0
    for request in month_requests:
        user_requests_info[request.creator_id]['used_requests'] += 1
        requests_amount += 1

    message = f'<b>База данных: {"🟢" if db_connect else "🔴"}</b>\n\n<b>Кэширование: {"🟢" if redis_connect else "🔴"}</b>\n\n<b>Использовано запросов в этом месяце:</b>\n'

    for id, data in user_requests_info.items():
        used_requests = data["used_requests"]
        if data["allowed_requests"] != None:
            allowed_requests = f'/{data["allowed_requests"]}'
        else:
            allowed_requests = ''
        user_name = data['name']
        
        message += f'{user_name}: {used_requests}{allowed_requests} шт.\n'

    message += f'<b>Всего: {requests_amount}/1000 шт.</b>'
    return message


async def DATABASE_ERROR(error):
    return f'Произошла ошибка с базой данных\n\nПодробнее: {error}'


async def ERROR(error):
    return f'Произошла ошибка\n\nПодробнее: {error}'