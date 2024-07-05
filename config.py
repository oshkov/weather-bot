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





# {"meta":{"message":"","code":"200"},"response":
#  {"items":[
# {"id":4368,"name":"Москва","nameP":"","url":"/weather-moscow-4368/","kind":"M","rate":0,"weight":0,"country":{"code":"RU","name":"Россия","nameP":""},"district":{"name":"Москва (город федерального значения)","nameP":""},"subDistrict":null},
# {"id":12906,"name":"Москва (Тушино)","nameP":"","url":"/weather-moscow-tushino-12906/","kind":"M","rate":0,"weight":0,"country":{"code":"RU","name":"Россия","nameP":""},"district":{"name":"Москва (город федерального значения)","nameP":""},"subDistrict":null},
# {"id":12905,"name":"Москва (Балчуг)","nameP":"","url":"/weather-moscow-balchug-12905/","kind":"M","rate":0,"weight":0,"country":{"code":"RU","name":"Россия","nameP":""},"district":{"name":"Москва (город федерального значения)","nameP":""},"subDistrict":null},
# {"id":13077,"name":"Москва (Внуково)","nameP":"","url":"/weather-moscow-vnukovo-13077/","kind":"A","rate":0,"weight":0,"country":{"code":"RU","name":"Россия","nameP":""},"district":{"name":"Москва (город федерального значения)","nameP":""},"subDistrict":{"name":"Внуковское (поселение)","nameP":""}},
# {"id":13068,"name":"Москва (Шереметьево)","nameP":"","url":"/weather-moscow-sheremetyevo-13068/","kind":"A","rate":0,"weight":0,"country":{"code":"RU","name":"Россия","nameP":""},"district":{"name":"Московская область","nameP":""},"subDistrict":{"name":"городской округ Химки","nameP":""}},
# {"id":13066,"name":"Москва (Домодедово)","nameP":"","url":"/weather-moscow-domodedovo-13066/","kind":"A","rate":0,"weight":0,"country":{"code":"RU","name":"Россия","nameP":""},"district":{"name":"Московская область","nameP":""},"subDistrict":{"name":"городской округ Домодедово","nameP":""}},
# {"id":13069,"name":"Москва (Остафьево)","nameP":"","url":"/weather-moscow-ostafyevo-13069/","kind":"A","rate":0,"weight":0,"country":{"code":"RU","name":"Россия","nameP":""},"district":{"name":"Москва (город федерального значения)","nameP":""},"subDistrict":{"name":"Рязановское (поселение)","nameP":""}},
# {"id":127729,"name":"Москвитино","nameP":"","url":"/weather-moskvitino-127729/","kind":"T","rate":0,"weight":0,"country":{"code":"RU","name":"Россия","nameP":""},"district":{"name":"Амурская область","nameP":""},"subDistrict":{"name":"Свободненский район","nameP":""}},
# {"id":99491,"name":"Москвитяновка","nameP":"","url":"/weather-moskvytianivka-99491/","kind":"T","rate":0,"weight":0,"country":{"code":"UA","name":"Украина","nameP":""},"district":{"name":"Хмельницкая область","nameP":""},"subDistrict":{"name":"Шепетовский район","nameP":""}},
# {"id":137216,"name":"Москвино","nameP":"","url":"/weather-moskvino-137216/","kind":"T","rate":0,"weight":0,"country":{"code":"RU","name":"Россия","nameP":""},"district":{"name":"Вологодская область","nameP":""},"subDistrict":{"name":"Вашкинский район","nameP":""}}],"total":10}}