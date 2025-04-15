import os
from dotenv import load_dotenv
import redis.asyncio as redis
import motor.motor_asyncio
import os
from urllib.parse import quote_plus  # Для экранирования спецсимволов в пароле


# Определяем путь к .env
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')

# Проверяем, существует ли файл .env
if not os.path.exists(env_path):
    print(f"⚠️  Файл .env не найден по пути: {env_path}")
else:
    load_dotenv(env_path)  # Загружаем переменные окружения


class ConnMongo:
    # Получение переменных окружения (атрибуты класса)
    MONGO_USER = os.getenv("MONGO_USER")
    MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
    MONGO_HOST = os.getenv("MONGO_HOST")
    MONGO_PORT = os.getenv("MONGO_PORT")

    @staticmethod
    async def connect_to_mongo():
        try:
            # Экранируем username и password на случай спецсимволов
            username = quote_plus(ConnMongo.MONGO_USER)
            password = quote_plus(ConnMongo.MONGO_PASSWORD)
            
            # Подключение к MongoDB на VPS
            connection_string = f"mongodb://{username}:{password}@{ConnMongo.MONGO_HOST}:{ConnMongo.MONGO_PORT}"
            
            client = motor.motor_asyncio.AsyncIOMotorClient(
                connection_string,
                serverSelectionTimeoutMS=5000  # Таймаут подключения
            )

            # Проверка подключения
            await client.admin.command('ping')
            print("Успешное подключение к MongoDB!")
            
            return client
            
        except Exception as e:
            print(f"Ошибка подключения к MongoDB: {e}")
            raise  # Пробрасываем исключение дальше


class ConnJwt:

    # Получение переменных окружения
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

    # Проверяем корректность подключения
    if not JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY не найден в переменных окружения")
    


class ConnRedis:

    # Получение переменных окружения (атрибуты класса)
    REDIS_AUTH_1_HOST = os.getenv('REDIS_AUTH_1_HOST')
    REDIS_AUTH_1_PORT = os.getenv('REDIS_AUTH_1_PORT')
    REDIS_AUTH_1_DB = os.getenv('REDIS_AUTH_1_DB')
    REDIS_AUTH_1_PASSWORD = os.getenv('REDIS_AUTH_1_PASSWORD')

    # Подключение к базе данных
    @staticmethod
    async def connection():
        try:
            conn = redis.Redis(
                host=ConnRedis.REDIS_AUTH_1_HOST,
                port=ConnRedis.REDIS_AUTH_1_PORT,
                db=ConnRedis.REDIS_AUTH_1_DB,
                password=ConnRedis.REDIS_AUTH_1_PASSWORD
            )
            
            # Проверка соединения
            if not conn:
                print("Ошибка: не удалось установить соединение с Redis")
                return False
            
            # Проверка, что соединение действительно работает
            await conn.ping()
            return conn
        
        except Exception as e:
            print(f"Ошибка при подключении к Redis: {e}")
            return False