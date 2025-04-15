from fastapi import Request, HTTPException
from app.config.Config import ConnMongo

class Recipient:
    
    @staticmethod
    async def recipient(request: Request, auth):
        # Получаем из JWT company_id
        current_company_id = auth["company_id"]

        # Получаем данные из запроса
        try:
            data = await request.json()
        except:
            raise HTTPException(400, "Переданы некорректные данные")
        
        sender_company_id = data.get("sender_company_id")
        status = data.get("status")

        # Проверка наличия обязательных полей
        if not sender_company_id or not status:
            raise HTTPException(400, "Обязательные поля отсутствуют: sender_company_id или status")
        
        # Проверка корректности статуса
        if status not in ("Активно", "Неактивно"):
            raise HTTPException(400, "Некорректный статус. Допустимые значения: 'Активно' или 'Неактивно'")

        # Проверяем, что текущая компания не является отправителем
        if current_company_id == sender_company_id:
            raise HTTPException(400, "Вы не можете обрабатывать свою собственную заявку")

        try:
            client = await ConnMongo.connect_to_mongo()
            if client is None:
                raise HTTPException(500, "Не удалось подключиться к MongoDB")

            db_partnerships = client["partnerships"]
            partnerships_collection = db_partnerships["partnerships"]

            # Ищем заявку где:
            # отправитель - sender_company_id, получатель - current_company_id И статус "Неактивно"
            partnership_filter = {
                "$or": [
                    {"company_a": sender_company_id, "company_b": current_company_id, "status": "Неактивно"},
                    {"company_a": current_company_id, "company_b": sender_company_id, "status": "Неактивно"}
                ]
            }

            existing_partnership = await partnerships_collection.find_one(partnership_filter)

            if not existing_partnership:
                raise HTTPException(404, "Заявка не найдена или уже обработана")

            # Обрабатываем заявку в зависимости от статуса
            if status == "Активно":
                await partnerships_collection.update_one(
                    {"_id": existing_partnership["_id"]},
                    {"$set": {"status": "Активно"}}
                )
                return {"message": "Заявка принята. Теперь вы партнеры"}
            
            elif status == "Неактивно":
                await partnerships_collection.delete_one({"_id": existing_partnership["_id"]})
                return {"message": "Заявка отклонена"}
            
        except HTTPException:
            raise  # Просто пробрасываем дальше
        except Exception as e:
            raise HTTPException(500, "Internal server error")
        finally:
            if client:
                client.close() 