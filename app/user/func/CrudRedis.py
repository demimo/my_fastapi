from datetime import timedelta


from app.config.Config import ConnRedis


class CrudRedis:

    # Функция для записи данных в Redis
    @staticmethod
    async def set(user_id: int, device_id: str, ip: str, ua: str, token: str):
        conn = None
        try:
            # Подключаемся к Redis
            conn = await ConnRedis.connection()

            # Формируем ключ и значение
            key = f"sessions:{user_id}:{device_id}"
            value = {'device_id': device_id, 'ip': ip, 'ua': ua, 'token': token}

            # Записываем в Redis
            await conn.hset(key, mapping=value)

            # Устанавливаем TTL (7 дней)
            ttl_seconds = int(timedelta(days=7).total_seconds())
            await conn.expire(key, ttl_seconds)

            return True

        except Exception as e:
            print(f"Error: {e}")
            return None


    # Функция для получения конкретной записи пользователя
    @staticmethod
    async def get(user_id: int, device_id: str):
        try:
            # Подключаемся к Redis
            conn = await ConnRedis.connection()

            # Формируем ключ
            key = f"sessions:{user_id}:{device_id}"

            # Получаем значение по ключу
            value = await conn.hget(key, 'token')

            # Если значение найдено, декодируем его из bytes в строку
            if value is not None:
                return value.decode('utf-8')  # Преобразуем байты в строку
            else:
                return None  # Если значение не найдено, возвращаем None
        
        except Exception as e:
            print(f"Error: {e}")
            return None
        

    # Удаление конкретной записи
    @staticmethod
    async def delete(user_id: int, device_id: str):
        try:
            # Подключаемся к Redis
            conn = await ConnRedis.connection()

            # Формируем ключ
            key = f"sessions:{user_id}:{device_id}"

            # Удаляем только конкретный токен
            deleted = await conn.delete(key)

            return deleted

        except Exception as e:
            print(f"Error: {e}")
            return None


    
    # Получение всех устройств
    @staticmethod
    async def getAll(user_id: int):

        try:
            # Подключаемся к Redis
            conn = await ConnRedis.connection()

            # Шаблон поиска
            pattern = f"sessions:{user_id}:*"

            cursor = b"0"
            sessions = []

            while cursor:
                cursor, keys = await conn.scan(cursor=cursor, match=pattern, count=100)
                for key in keys:
                    # Получаем всю хеш-таблицу
                    data = await conn.hgetall(key)
                    if data:
                        sessions.append({
                            "ip": data.get(b"ip").decode("utf-8") if b"ip" in data else None,
                            "ua": data.get(b"ua").decode("utf-8") if b"ua" in data else None
                        })
                        
            # Возвращаем список словарей с IP и UA
            return sessions

        except Exception as e:
            print(f"Error: {e}")
            return None
        

    # Удаление всех записей пользователя
    @staticmethod
    async def deleteAll(user_id: int):
        conn = None
        try:
            # Подключаемся к Redis
            conn = await ConnRedis.connection()
            
            # Шаблон для поиска ключей сессий пользователя
            pattern = f"sessions:{user_id}:*"
            cursor = 0  # Начинаем с курсора 0
            deleted_count = 0

            while True:
                # Используем SCAN для итерации по ключам
                cursor, keys = await conn.scan(cursor, match=pattern, count=100)
                
                if keys:
                    # Удаляем все найденные ключи за одну операцию
                    await conn.delete(*keys)
                    deleted_count += len(keys)
                
                # Завершаем цикл когда cursor возвращается к 0
                if cursor == 0:
                    break

            return deleted_count > 0  # True если что-то удалили

        except Exception as e:
            print(f"Error in deleteAll: {e}")
            return False
        finally:
            if conn:
                await conn.close()