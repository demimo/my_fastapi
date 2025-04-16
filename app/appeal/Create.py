from fastapi import Request, HTTPException
from bson import ObjectId
import datetime

from app.config.Config import ConnMongo

class Create:
    @staticmethod
    async def create(request: Request, auth):

        # Получаем данные из JWT
        current_user_id = auth["user_id"]
        current_company_id = auth["company_id"]
        
        # Получаем данные с формы:
        try:
            data = await request.json()
        except:
            raise HTTPException(400, "Переданы некорректные данные")
            
        target_subject = data.get("subject")
        target_priority = data.get("priority")
        target_responsible_company_id = data.get("responsible_company_id")

        # Обрабатываем участников (исправлено на target_participants)
        participants = {
            "company_id": data.get("target_participants", {}).get("company_id", []),
            "user_id": data.get("target_participants", {}).get("user_id", [])
        }

        # Проверка обязательных полей
        if not target_subject:
            raise HTTPException(400, "Поле subject обязательно")
        if not target_priority:
            raise HTTPException(400, "Поле priority обязательно")
        if not target_responsible_company_id:
            raise HTTPException(400, "Поле responsible_company_id обязательно")
        
        
        try:

            # Подключение к базе
            client = await ConnMongo.connect_to_mongo()
            if client is None:
                raise HTTPException(500, "Не удалось подключиться к MongoDB")
                
            appeals_db = client["appeals"]
            appeals_collection = appeals_db["appeals"]

            # Добавляем данные
            await appeals_collection.insert_one({
                "subject": target_subject,
                "status": "Открыто",
                "priority": target_priority,
                "creator_company_id": current_company_id,
                "creator_user_id": current_user_id,
                "responsible_company_id": target_responsible_company_id,
                "participants": participants,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            })

            return {"message": "Обращение создано"}

        except HTTPException:
            raise  # Просто пробрасываем дальше
        except Exception as e:
            raise HTTPException(500, "Internal server error")
        finally:
            if client:
                client.close()