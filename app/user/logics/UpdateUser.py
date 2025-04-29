from fastapi import Request, HTTPException
import bcrypt
from bson import ObjectId

from app.config.Config import ConnMongo
from app.user.logics.ResetAllSession import ResetAllSession


class UpdateUser:

    @staticmethod
    async def update_user(request: Request, auth):

        # Получаем данные из JWT
        current_user_id = auth["user_id"]
        current_company_id = auth["company_id"]
        current_role = auth["role"]
        current_is_active = auth["is_active"]
        
        # Получаем данные с формы
        try:
            data = await request.json()
        except:
            raise HTTPException(400, "Переданы некорректные данные")
        target_id = data.get("id")
        target_user_name = data.get("name")
        target_email = data.get("email")
        target_password = data.get("password")
        target_role = data.get("role")
        target_is_active = data.get("is_active")
        target_delete = data.get("delete")

        if not target_id:
            raise HTTPException(400, "Выберите пользователя для редактирования")

        # Подключаемся к базе
        try:
            client = await ConnMongo.connect_to_mongo()
            if client is None:
                raise HTTPException(500, "Не удалось подключиться к MongoDB")

            users_db = client["users"]
            users_collection = users_db["users"]

            # Проверяем целевого пользователя
            check_target_user = await users_collection.find_one({"_id": ObjectId(target_id)})

            if not check_target_user:
                raise HTTPException(404, "Пользователь не найден")

            if current_company_id != check_target_user["company_id"]:
                raise HTTPException(403, "Пользователь не из вашей компании")
            
            if (current_role != 'Владелец') and (target_role == 'Владелец'):
                    raise HTTPException(403, "Вы не можете назначить пользователя владельцем")

            # Редактирование своего профиля
            if current_user_id == target_id:

                if target_delete:
                    raise HTTPException(403, "Вы не можете себя удалить")
                
                if current_role != target_role:
                    raise HTTPException(403, "Вы не можете изменить себе права")

                if current_is_active != target_is_active:
                    raise HTTPException(403, "Вы не можете себя деактивировать")
                
            # Редактирование других профилей
            if current_user_id != target_id:

                if check_target_user["role"] == 'Владелец':
                    raise HTTPException(403, "Вы не можете редактировать профиль владельца")
                
                if current_role == 'Владелец' and target_role == 'Владелец':
                    raise HTTPException(403, "Вы не можете назначить пользователя владельцем")
                
                if current_role == 'Администратор' and check_target_user["role"] == 'Администратор':
                    raise HTTPException(403, "Вы не можете редактировать профиль администратора")
                
                if current_role == 'Пользователь' and check_target_user["role"] == 'Пользователь':
                    raise HTTPException(403, "Вы не можете редактировать профиль пользователя")
                
                if current_role == 'Пользователь' and check_target_user["role"] == 'Администратор':
                    raise HTTPException(403, "Вы не можете редактировать профиль администратора")
                    
            # Изменяем имя
            if target_user_name != check_target_user["name"]:

                await users_collection.update_one(
                    {"_id": check_target_user["_id"]},
                    {"$set": {"name": target_user_name}}
                )

            # Изменяем email
            if target_email != check_target_user["email"]:
                
                # Проверяем на дубль
                existing_email = await users_collection.find_one({"email": target_email})
                if existing_email:
                    raise HTTPException(400, "Пользователь с таким email уже существует")
                
                await users_collection.update_one(
                    {"_id": check_target_user["_id"]},
                    {"$set": {"email": target_email}}
                )

            # Изменяем пароль
            if target_password:

                # Хеширование пароля
                target_password = target_password.encode()
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(target_password, salt).decode('utf-8')

                await users_collection.update_one(
                    {"_id": check_target_user["_id"]},
                    {"$set": {"hashed_password": hashed_password}}
                )

                # Удаляем все сессии
                await ResetAllSession.reset(target_id)

            # Изменяем роль
            if target_role != check_target_user["role"]:

                await users_collection.update_one(
                    {"_id": check_target_user["_id"]},
                    {"$set": {"role": target_role}}
                )

                # Удаляем все сессии
                await ResetAllSession.reset(target_id)

            # Изменяем активность
            if target_is_active != check_target_user["is_active"]:

                await users_collection.update_one(
                    {"_id": check_target_user["_id"]},
                    {"$set": {"is_active": target_is_active}}
                )

                # Удаляем все сессии
                await ResetAllSession.reset(target_id)

            # Удалить
            if target_delete:

                # Удаляем пользователя с таблицы пользователей
                await users_collection.delete_one({"_id": check_target_user["_id"]})

                # Удаляем все сессии
                await ResetAllSession.reset(target_id)

            return {"message": "Изменения внесены"}
                
        except HTTPException:
            raise  # Просто пробрасываем дальше
        except Exception as e:
            raise HTTPException(500, "Internal server error")
        finally:
            if client:
                client.close()     
            