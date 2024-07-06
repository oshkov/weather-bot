from dotenv import load_dotenv
import os


load_dotenv()


BOT_TOKEN = os.environ.get('BOT_TOKEN')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
GISMETEO_API_TOKEN = os.environ.get('GISMETEO_API_TOKEN')
USERS = os.environ.get('USERS').split(', ')