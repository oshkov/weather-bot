import json

# Открытие конфига из JSON-файла
def load_config(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
    return config

config = load_config('config.json')['config-prod']

DB_HOST = config['db_host']
DB_PORT = config['db_port']
DB_NAME = config['db_name']
DB_USER = config['db_user']
DB_PASSWORD = config['db_password']
BOT_TOKEN = config['bot_token']
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
GISMETEO_API_TOKEN = config['gismeteo_api_token']
REDIS_HOST = config['redis_host']
REDIS_PORT = config['redis_port']
REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}'
USERS = config['users']