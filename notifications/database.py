from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select, and_
import datetime
import pytz
import json


from models import UserModel, RequestModel


class Database:
    '''
    Класс для работы с базой данных
    '''

    # Инициализация
    def __init__(self, db_url):
        self.engine = create_async_engine(db_url)
        self.async_session = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)


    # Создание сессии
    async def get_session(self):
        async with self.async_session() as session:
            yield session


    # Кэширование ответа
    async def create_cache(self, session, creator_id, city_id, request_type, json_response):
        try:
            # Определение типа запроса
            if request_type in ['today', 'tomorrow', '10-days']:
                # Запрос расширенной погоды
                request_type = 'extended_weather'

            elif request_type == 'now':
                # Запрос текущей погоды
                request_type = 'current_weather'

            elif request_type == 'cities':
                # Запрос городов
                request_type = request_type

            filename = f'{datetime.datetime.now(pytz.timezone("Europe/Moscow")).strftime("%Y-%m-%d_%H-%M-%S")}.json'

            with open(f'cached_responses/{filename}', 'w', encoding='utf-8') as file:
                json.dump(json_response, file, ensure_ascii=False, indent=4)

            # Запись в базу данных
            request_info = RequestModel(
                creation_time = datetime.datetime.now(pytz.timezone('Europe/Moscow')),
                creator_id = str(creator_id),
                city_id = city_id,
                request_type = request_type,
                response_filename = filename
            )

            # Добавление данных в сессию
            session.add(request_info)

            # Сохранение данных в бд
            await session.commit()

            return True

        except Exception as error:
            print(f'create_cache() error: {error}')
            return False


    # Проверка на наличие актуального кэшированного ответа в базе данных
    async def check_cache(self, session, city_id, request_type):
        try:
            if request_type in ['today', 'tomorrow', '10-days']:
                request_type = 'extended_weather'

                # Определение времени в 6 часов
                timedelta = datetime.datetime.now(pytz.timezone('Europe/Moscow')) - datetime.timedelta(hours=6)

            elif request_type == 'now':
                request_type = 'current_weather'

                # Определение времени в 1 час
                timedelta = datetime.datetime.now(pytz.timezone('Europe/Moscow')) - datetime.timedelta(hours=1)

            elif request_type == 'cities':
                request_type = request_type

                # Установка времени в очень далекое прошлое на 100 лет назад
                timedelta = datetime.datetime(1900, 1, 1, tzinfo=pytz.timezone('Europe/Moscow'))

            # Получение ответа
            cached_repsonse = await session.execute(
                select(RequestModel.response_filename)
                    .where(
                        and_(
                            RequestModel.request_type == request_type,
                            RequestModel.city_id == city_id,
                            RequestModel.creation_time > timedelta
                        ),
                    )
                )
            cached_repsonse = [row for row in cached_repsonse.scalars()]

            # Вывод последнего ответа, при его наличии
            if len(cached_repsonse) == 0:
                return None

            else:
                filename = cached_repsonse[-1]

                # В случае наличии записи в бд, но остутствии файла
                if filename is None:
                    return None

                # Получение данных из файла
                with open(f'cached_responses/{filename}', 'r', encoding='utf-8') as file:
                    data = json.load(file)

                return data

        except Exception as error:
            print(f'check_cache() error: {error}')


    # Получение списка пользователей у кого включены уведомления
    async def get_users_with_notifications(self, session):
        try:
            users = await session.execute(
                select(UserModel)
                    .where(
                        UserModel.notification_status == 1
                    )
                )
            users = [row for row in users.scalars()]

            # Вывод ответа, при его наличии
            if len(users) == 0:
                return None
            else:
                return users

        except Exception as error:
            print(f'get_users_with_notifications() error: {error}')