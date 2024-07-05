import datetime


weekdays = ['Пн','Вт','Ср','Чт','Пт','Сб','Вс']
months = ['Января','Февраля','Марта','Апреля','Мая','Июня','Июля','Августа','Сентября','Октября','Ноября','Декабря']


ERROR_START = 'Произошла ошибка, попробуйте ещё раз'
WRITE_CITY = 'Напиши название города, в котором хочешь узнать погоду'
SELECT_CITY = 'Выбери город из предложенных'
SELECT_CITY_ERROR = 'Произошла ошибка: город не найден\nВведи название города заново'
SUCCESS_CITY_CONNECTED = '✅ Город успешно привязан к вашему аккаунту'
ERROR_CITY_CONNECTED = 'Произошла ошибка, не удалось привязать город к вашему аккаунту'
ABOUT = 'Этот приватный бот создан по личной инициативе @oshkov\n\nБот использует официальное API от <a href="https://www.gismeteo.ru/">Gismeteo</a>'
NOTIFICATION_ON = 'Уведомления включены🔔\n\nВы будете получать уведомления в 7.00 и 21.00 по мск каждый день'
NOTIFICATION_OFF = 'Уведомления выключены🔕'
LOADING = 'Загрузка данных...'


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
    date = data[0]['date']['local']
    date_obj = datetime.datetime.strptime(str(date), "%Y-%m-%dT%H:%M:%SZ")
    weekday = weekdays[date_obj.weekday()]
    day = date_obj.day
    month = months[date_obj.month - 1]
    date_today = f'{weekday}, {day} {month}'

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

    return f'Погода {name_p} сегодня ({date_today}):\n\n<b>{times[0]}:</b> {emojis[0]} {temperatures[0]}°, {descriptions[0]}, {wind_speeds[0]} м/с\n<b>{times[1]}:</b> {emojis[1]} {temperatures[1]}°, {descriptions[1]}, {wind_speeds[1]} м/с\n<b>{times[2]}:</b> {emojis[2]} {temperatures[2]}°, {descriptions[2]}, {wind_speeds[2]} м/с\n<b>{times[3]}:</b> {emojis[3]} {temperatures[3]}°, {descriptions[3]}, {wind_speeds[3]} м/с\n<b>{times[4]}:</b> {emojis[4]} {temperatures[4]}°, {descriptions[4]}, {wind_speeds[4]} м/с\n<b>{times[5]}:</b> {emojis[5]} {temperatures[5]}°, {descriptions[5]}, {wind_speeds[5]} м/с'


async def WEATHER_TOMORROW(weather):
    # Данные о погоде
    data = weather['data']

    # Название города в предложном падеже
    name_p = data[0]['city']['nameP']

    # Обработка даты сегодня в формат: Вт, 5 марта
    date = data[9]['date']['local']
    date_obj = datetime.datetime.strptime(str(date), "%Y-%m-%dT%H:%M:%SZ")
    weekday = weekdays[date_obj.weekday()]
    day = date_obj.day
    month = months[date_obj.month - 1]
    date_tomorrow = f'{weekday}, {day} {month}'

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

    return f'Погода {name_p} завтра ({date_tomorrow}):\n\n<b>{times[0]}:</b> {emojis[0]} {temperatures[0]}°, {descriptions[0]}, {wind_speeds[0]} м/с\n<b>{times[1]}:</b> {emojis[1]} {temperatures[1]}°, {descriptions[1]}, {wind_speeds[1]} м/с\n<b>{times[2]}:</b> {emojis[2]} {temperatures[2]}°, {descriptions[2]}, {wind_speeds[2]} м/с\n<b>{times[3]}:</b> {emojis[3]} {temperatures[3]}°, {descriptions[3]}, {wind_speeds[3]} м/с\n<b>{times[4]}:</b> {emojis[4]} {temperatures[4]}°, {descriptions[4]}, {wind_speeds[4]} м/с\n<b>{times[5]}:</b> {emojis[5]} {temperatures[5]}°, {descriptions[5]}, {wind_speeds[5]} м/с'


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
        date = data[index]['date']['local']
        date_obj = datetime.datetime.strptime(str(date), "%Y-%m-%dT%H:%M:%SZ")
        weekday = weekdays[date_obj.weekday()]
        day = date_obj.day
        month = months[date_obj.month - 1]
        dates.append(f'{weekday}, {day} {month}')

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