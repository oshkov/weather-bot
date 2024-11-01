import aioredis
import json


class Cache:
    '''
    Класс для работы с кэшем
    '''

    # Инициализация
    def __init__(self, REDIS_URL):
        self.redis_client = aioredis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=1)

    # Запись кэша
    async def create_cache(self, city_id, request_type, json_response):
        try:
            if request_type in ['today', 'tomorrow', '10-days']:
                request_type = 'extended_weather'
                ttl = 21600     # Время жизни кэша для расширенных запросов 6 часов

            elif request_type == 'now':
                request_type = 'current_weather'
                ttl = 3600      # Время жизни кэша для запросов на данный момент 1 час

            elif request_type == 'cities':
                request_type = request_type
                ttl = 31536000      # Время жизни кэша для запросов города 1 год

            cache_key = f'{city_id}_{request_type}'
            await self.redis_client.setex(cache_key, ttl, json.dumps(json_response))
            print(f'Кэш записан: {cache_key}')

        except Exception as error:
            print(f'create_cache() error: {error}')
            return False
        
    # Проверка на наличие кэшированного ответа
    async def check_cache(self, city_id, request_type):
        try:
            if request_type in ['today', 'tomorrow', '10-days']:
                request_type = 'extended_weather'

            elif request_type == 'now':
                request_type = 'current_weather'

            elif request_type == 'cities':
                request_type = request_type

            cache_key = f'{city_id}_{request_type}'

            cached_response = await self.redis_client.get(cache_key)

            if cached_response:
                print(f'Кэш получен: {cache_key}')
                return json.loads(cached_response)
            else:
                return None

        except Exception as error:
            print(f'check_cache() error: {error}')

    # Проверка работы Redis
    async def check_connect(self):
        try:
            await self.redis_client.ping()
            return True
        except:
            return False