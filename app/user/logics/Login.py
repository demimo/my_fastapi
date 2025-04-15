from fastapi import Request, Response, HTTPException
import uuid
import bcrypt

from app.config.Config import ConnMongo
from app.user.func.CrudJwt import CrudJwt
from app.user.func.CrudRedis import CrudRedis


class Login:

    @staticmethod
    async def login(request: Request, response: Response):

        # Получаем данные с формы
        try:
            data = await request.json()
        except:
            raise HTTPException(400, "Переданы некорректные данные")
        
        user_email = data.get("email")
        user_pass = data.get("password")
        if not all([user_email, user_pass]):
            raise HTTPException(400, "Все поля обязательны")
        
        # Подключаемся к базе
        try:
            client = await ConnMongo.connect_to_mongo()
            if client is None:
                raise HTTPException(500, "Не удалось подключиться к MongoDB")

            users_db = client["users"]
            users_collection = users_db["users"]

            # Проверяем существует ли пользователь с таким email и активен ли он
            existing_user = await users_collection.find_one({"email": user_email})

            if not existing_user:
                raise HTTPException(404, "Неверный email или пароль")
            
            # Проверка пароля
            if bcrypt.checkpw(user_pass.encode(), existing_user["hashed_password"].encode()) == False:
                raise HTTPException(status_code=401, detail="Неверный email или пароль")

            if existing_user["is_active"] != "Активен":
                raise HTTPException(403, "Аккаунт не активен")
             
            # Сбор данных клиента
            device_id = str(uuid.uuid4())
            ip = request.client.host
            ua = request.headers.get("user-agent", "Unknown Browser")
            token = await CrudJwt.create_token(
                str(existing_user["_id"]),
                existing_user["company_id"],
                existing_user["role"],
                existing_user["is_active"],
                device_id, ip, ua
            )

            # Записываем сессию пользователя в Redis
            await CrudRedis.set(str(existing_user["_id"]), device_id, ip, ua, token)

            # Устанавливаем sessionid в cookies
            response.set_cookie(
                key="sessionid",  # Имя куки
                value=token,  # Значение куки (уникальный идентификатор сессии)
                max_age=36000,  # Время жизни куки — 1 час
                httponly=True,  # Куки доступны только на стороне сервера
                samesite="Strict"  # Защита от CSRF-атак
                # secure=True
            )

            return {"message": "Вход совершен"}
        
        except HTTPException:
            raise  # Просто пробрасываем дальше
        except Exception as e:
            raise HTTPException(500, "Internal server error")
        finally:
            if client:
                client.close()