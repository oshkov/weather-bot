import datetime


weekdays = ['Пн','Вт','Ср','Чт','Пт','Сб','Вс']
months = ['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря']


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