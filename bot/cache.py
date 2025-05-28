import aioredis
import json
import logging


class Cache:
    '''Класс для работы с кэшем'''

    def __init__(self, REDIS_URL):
        '''Инициализация'''

        self.redis_client = aioredis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=1)


    async def create_cache(self, city_id, request_type, json_response):
        '''Запись кэша'''

        try:
            # Проверка подключения к редис
            if not await self.check_connect():
                logging.error(f'Redis выключен!')
                return

            if request_type in ['today', 'tomorrow', '10-days']:
                request_type = 'extended_weather'
                ttl = 21600     # Время жизни кэша для расширенных запросов 6 часов

            elif request_type == 'now':
                request_type = 'current_weather'
                ttl = 3600      # Время жизни кэша для запросов на данный момент 1 час

            elif request_type == 'cities':
                request_type = request_type
                ttl = 31536000      # Время жизни кэша для запросов города 1 год

            else:
                logging.error(f'create_cache(): request_type is invalid')
                return False

            cache_key = f'{city_id}_{request_type}'
            await self.redis_client.setex(cache_key, ttl, json.dumps(json_response))
            logging.info(f'Кэш записан: {cache_key}')

        except Exception as error:
            logging.error(f'create_cache(): {error}')


    async def check_cache(self, city_id, request_type):
        '''Проверка на наличие кэшированного ответа'''

        try:
            # Проверка подключения к редис
            if not await self.check_connect():
                logging.error(f'Redis выключен!')
                return None

            if request_type in ['today', 'tomorrow', '10-days']:
                request_type = 'extended_weather'

            elif request_type == 'now':
                request_type = 'current_weather'

            elif request_type == 'cities':
                request_type = request_type

            cache_key = f'{city_id}_{request_type}'

            cached_response = await self.redis_client.get(cache_key)

            if cached_response:
                logging.info(f'Кэш получен: {cache_key}')
                return json.loads(cached_response)
            else:
                return None

        except Exception as error:
            logging.error(f'check_cache(): {error}')


    async def check_connect(self):
        '''Проверка работы Redis'''

        try:
            await self.redis_client.ping()
            return True
        except:
            return False