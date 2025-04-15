from fastapi import Request, HTTPException
import bcrypt

from app.config.Config import ConnMongo


class CreateUser:

    @staticmethod
    async def create(request: Request, auth):

        # Получаем данные из JWT
        current_company_id = auth["company_id"]
        current_role = auth["role"]

        # Проверка наличия прав на создание пользвователя
        if current_role == 'Пользователь':
            raise HTTPException(status_code=403, detail="У вас нет прав на создание пользователя")
        
        # Получаем данные с формы:
        try:
            data = await request.json()
        except:
            raise HTTPException(400, "Переданы некорректные данные")
        target_name = data.get("name")
        target_email = data.get("email")
        target_password = data.get("password")
        target_role = data.get("role")

        # Корректность данных
        if not target_name or not target_email or not target_password or not target_role:
            raise HTTPException(status_code=400, detail="Все поля обязательны")
        if target_role != 'Администратор' and target_role != 'Пользователь':
            raise HTTPException(status_code=400, detail="Введена не верно роль")

        try:

            # Подключение к базе
            client = await ConnMongo.connect_to_mongo()
            if client is None:
                raise HTTPException(500, "Не удалось подключиться к MongoDB")
                
            users_db = client["users"]
            users_collection = users_db["users"]
            
            existing_user = await users_collection.find_one({"email": target_email})
            if existing_user:
                raise HTTPException(400, "Пользователь с таким email уже существует")

            # Хеширование пароля
            target_password = target_password.encode()
            salt = bcrypt.gensalt()
            target_hashed_password = bcrypt.hashpw(target_password, salt).decode('utf-8')

            # Формируем объект
            user_data = {
                "name": target_name,
                "email": target_email,
                "hashed_password": target_hashed_password,
                "role": target_role,
                "company_id": current_company_id,
                "is_active": "Активен"
            }

            # Добавляем данные
            await users_collection.insert_one(user_data)

            return {"message": "Регистрация пользователя успешно завершена"}
            
        except HTTPException:
            raise  # Просто пробрасываем дальше
        except Exception as e:
            raise HTTPException(500, "Internal server error")
        finally:
            if client:
                client.close()