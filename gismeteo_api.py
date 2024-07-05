import requests
import json
import config


class Gismeteo:
    '''
    Этот класс предоставляет методы для взаимодействия с GismeteoAPI
    '''

    def __init__(self, token):
        self.token = token


    def get_cities(self, query):
        '''
        Поиск городов

        :param query: запрос.
        '''

        request = f'https://api.gismeteo.net/v2/search/cities/?query={query}'
        headers = {'X-Gismeteo-Token': self.token}

        # Отправка GET-запроса
        response = requests.get(request, headers=headers)

        return response


    def get_weather(self, city_id, request_type):
        '''
        Получение данных о погоде на текущий момент

        :param city_id: id города.
        '''

        if request_type == 'now':
            request = f'https://api.gismeteo.net/v3/weather/current/?city_id={city_id}'
        else:
            request = f'https://api.gismeteo.net/v3/weather/forecast/h3/?city_id={city_id}'

        headers = {'X-Gismeteo-Token': self.token}

        # Отправка GET-запроса
        response = requests.get(request, headers=headers)

        return response