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
    async def create_request(self, session, creator_id, city_id, request_type, json_response):
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

            # Запись в базу данных
            request_info = RequestModel(
                creation_time = datetime.datetime.now(pytz.timezone('Europe/Moscow')),
                creator_id = str(creator_id),
                city_id = city_id,
                request_type = request_type,
                response_filename = None
            )

            # Добавление данных в сессию
            session.add(request_info)

            # Сохранение данных в бд
            await session.commit()

            return True

        except Exception as error:
            print(f'create_request() error: {error}')
            return False


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