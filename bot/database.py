from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select, and_
from models import UserModel, RequestModel, Base
import datetime
import pytz
import logging


class DatabaseError(Exception):
    '''Исключение для ошибок в базе данных'''
    
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class Database:
    '''Класс для работы с базой данных'''

    def __init__(self, db_url):
        '''Инициализация'''

        self.engine = create_async_engine(db_url)
        self.async_session = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)


    async def init_tables(self):
        '''Создание таблиц в бд'''

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


    async def get_session(self):
        '''Создание сессии'''

        async with self.async_session() as session:
            yield session
        

    async def add_city(self, session, message, city_id, city_name, city_url):
        '''Привязка города к пользователю'''

        try:
            user = await session.get(UserModel, str(message.from_user.id))
            user.city = city_name
            user.city_id = city_id
            user.city_url = city_url

            # Добавление данных в бд и сохранение
            await session.commit()

            return True

        except Exception as error:
            logging.error(f'add_city() error: {error}')
            raise DatabaseError(error)
        

    async def get_user_information(self, session, callback):
        '''Получение данных о пользователе'''

        try:
            user = await session.get(UserModel, str(callback.from_user.id))

            # Возвращается объект анкеты, в случае отсутствия None
            return user

        except Exception as error:
            logging.error(f'get_user_information() error: {error}')
            raise DatabaseError(error)


    async def create_request(self, session, creator_id, city_id, request_type):
        '''Сохранение запроса в бд'''

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
                request_type = request_type
            )

            # Добавление данных в сессию
            session.add(request_info)

            # Сохранение данных в бд
            await session.commit()

        except Exception as error:
            logging.error(f'create_request() error: {error}')
            raise DatabaseError(error)


    async def get_users_with_notifications(self, session):
        '''Получение списка пользователей у кого включены уведомления'''

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
            logging.error(f'get_users_with_notifications() error: {error}')
            raise DatabaseError(error)


    async def check_allowed_requests(self, session, user_id):
        '''Проверить лимит запросов пользователя в этом месяце'''

        try:
            # Получение количества разрешенных запросов для пользователя
            user = await session.get(UserModel, str(user_id))
            allowed_requests = user.allowed_requests

            if allowed_requests == None:
                return True

            # Начало текущего месяца
            now = datetime.datetime.now()
            this_month_start = datetime.datetime(now.year, now.month, 1)

            # Получение количества запросов пользователя в этом месяце
            requests_this_month = await session.execute(
                select(RequestModel)
                    .where(
                        RequestModel.creator_id == str(user_id),
                        RequestModel.creation_time > this_month_start
                    )
                )
            requests_this_month = [row for row in requests_this_month.scalars()]

            if len(requests_this_month) < allowed_requests:
                return True
            else:
                return False

        except Exception as error:
            logging.error(f'check_allowed_requests() error: {error}')
            raise DatabaseError(error)


    async def get_month_requests(self, session):
        '''Получение всех запросов за месяц'''

        try:
            # Начало текущего месяца
            now = datetime.datetime.now()
            this_month_start = datetime.datetime(now.year, now.month, 1)

            month_requests = await session.execute(
                select(RequestModel)
                    .where(
                        RequestModel.creation_time > this_month_start
                    )
                )
            month_requests = [row for row in month_requests.scalars()]

            return month_requests

        except Exception as error:
            logging.error(f'get_month_requests() error: {error}')
            raise DatabaseError(error)


    async def get_all_users(self, session):
        '''Получение всех пользователей'''

        try:
            users = await session.execute(select(UserModel))
            users = [row for row in users.scalars()]

            return users

        except Exception as error:
            logging.error(f'get_all_users() error: {error}')
            raise DatabaseError(error)