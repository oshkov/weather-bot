import json
from dotenv import load_dotenv
import os


load_dotenv()

def load_json(file_path):
    '''Открытие JSON-файла'''

    with open(file_path, 'r', encoding='utf-8') as file:
        config = json.load(file)

    return config


BOT_TOKEN = os.environ.get('bot_token')
DATABASE_URL = os.environ.get('database_path')
REDIS_URL = os.environ.get('redis_url')
GISMETEO_API_TOKEN = os.environ.get('gismeteo_api_token')
USERS_JSON = os.environ.get('users_json_path')

USERS = load_json(USERS_JSON)['users']