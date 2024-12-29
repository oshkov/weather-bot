import json

# Открытие конфига из JSON-файла
def load_config(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
    return config

config = load_config('config.json')['config-prod']

PATH_TO_DB = config['path_to_db']
BOT_TOKEN = config['bot_token']
DATABASE_URL = f"sqlite+aiosqlite:////{PATH_TO_DB}weather_bot.db"
GISMETEO_API_TOKEN = config['gismeteo_api_token']
REDIS_HOST = config['redis_host']
REDIS_PORT = config['redis_port']
REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}'
USERS = config['users']