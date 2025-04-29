from fastapi import HTTPException

from app.config.Config import ConnMongo

class GetAll:

    @staticmethod
    async def get_all(auth):
        # Получаем данные из JWT
        current_company_id = auth["company_id"]

        try:
            # Подключаемся к MongoDB
            client = await ConnMongo.connect_to_mongo()
            if client is None:
                raise HTTPException(status_code=500, detail="Не удалось подключиться к MongoDB")

            db_users = client["users"]
            users_collection = db_users["users"]

            # Ищем все активные обращения, где текущая компания является ответственной
            user_cursor = users_collection.find({
                "company_id": current_company_id
            })

            users = await user_cursor.to_list(length=None)

            if not users:
                return {"message": "Пользователи не найдены"}

            # Формируем список обращений
            users_list = []
            for user in users:
                try:
                    user_data = {
                        "_id": str(user.get("_id", "")),
                        "name": user.get("name", ""),
                        "email": user.get("email", ""),
                        "role": user.get("role", ""),
                        "company_id": str(user.get("responsible_company_id", "")),
                        "is_active": user.get("is_active", ""),
                    }
                    users_list.append(user_data)
                except Exception as e:
                    continue  # Пропускаем проблемные записи

            return {
                "message": "Пользователи успешно найдены",
                "count": len(users_list),
                "users": users_list
            }


        except HTTPException:
            raise  # Просто пробрасываем дальше
        except Exception as e:
            raise HTTPException(500, "Internal server error")
        finally:
            if client:
                client.close() 