from fastapi import Request, Response, HTTPException
import uuid
import bcrypt

from app.config.Config import ConnMongo
from app.user.func.CrudJwt import CrudJwt
from app.user.func.CrudRedis import CrudRedis

class Registration:

    @staticmethod
    async def registration(request: Request, response: Response):

        try:
            data = await request.json()
        except:
            raise HTTPException(400, "Переданы некорректные данные")
        
        company_name = data.get("company_name")
        user_name = data.get("user_name")
        user_email = data.get("email")
        user_pass = data.get("password")

        if not all([company_name, user_name, user_email, user_pass]):
            raise HTTPException(400, "Все поля обязательны")
        
        try:
            client = await ConnMongo.connect_to_mongo()
            if client is None:
                raise HTTPException(500, "Не удалось подключиться к MongoDB")
                
            db = client["companies"]
            companies_collection = db["companies"]
            users_db = client["users"]
            users_collection = users_db["users"]

            existing_company = await companies_collection.find_one({"name": company_name})
            if existing_company:
                raise HTTPException(400, "Компания уже существует")
            
            existing_user = await users_collection.find_one({"email": user_email})
            if existing_user:
                raise HTTPException(400, "Пользователь с таким email уже существует")

            company_result = await companies_collection.insert_one({"name": company_name})
            company_id = str(company_result.inserted_id)

            password = user_pass.encode()
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password, salt).decode('utf-8')

            user_data = {
                "name": user_name,
                "email": user_email,
                "hashed_password": hashed_password,
                "role": "Владелец",
                "company_id": company_id,
                "is_active": "Активен"
            }

            user_result = await users_collection.insert_one(user_data)
            user_id = str(user_result.inserted_id)

            # Формируем JWT токен
            device_id = str(uuid.uuid4())
            ip = request.client.host
            ua = request.headers.get("user-agent", "Unknown Browser")
            token = await CrudJwt.create_token(user_id, company_id, user_data["role"], user_data["is_active"], device_id, ip, ua)

            # Записываем сессию пользователя в Redis
            await CrudRedis.set(user_id, device_id, ip, ua, token)
            
            # Устанавливаем sessionid в cookies
            response.set_cookie(
                key="sessionid",  # Имя куки
                value=token,  # Значение куки (уникальный идентификатор сессии)
                max_age=36000,  # Время жизни куки — 1 час
                httponly=True,  # Куки доступны только на стороне сервера
                samesite="Strict"  # Защита от CSRF-атак
                # secure=True
            )

            return {"message": "Регистрация успешно завершена"}
            
        except HTTPException:
            raise  # Просто пробрасываем дальше
        except Exception as e:
            raise HTTPException(500, "Internal server error")
        finally:
            if client:
                client.close()