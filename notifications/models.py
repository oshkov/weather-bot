from sqlalchemy import Column, Integer, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class UserModel(Base):
    '''
    Модель таблицы для хранения данных пользователей
    '''

    __tablename__ = 'users'

    enter = Column(TIMESTAMP(timezone=True))
    id = Column(Text, primary_key=True)
    username = Column(Text)
    name = Column(Text)
    lastname = Column(Text)
    allowed_requests = Column(Integer)
    city = Column(Text)
    city_id = Column(Text)
    city_url = Column(Text)
    notification_status = Column(Integer)


class RequestModel(Base):
    '''
    Модель таблицы для хранение ответов от GismeteoAPI
    '''

    __tablename__ = 'requests'

    creation_time = Column(TIMESTAMP(timezone=True))
    creator_id = Column(Text, primary_key=True)
    city_id = Column(Text)
    request_type = Column(Text)
    response_filename = Column(Text)