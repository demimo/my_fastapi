from fastapi import Request, HTTPException
from bson import ObjectId

from app.config.Config import ConnMongo

class Sender:
    
    @staticmethod
    async def sender(request: Request, auth):

        client = None

        sender_company_id = auth["company_id"]

        try:
            data = await request.json()
        except:
            raise HTTPException(400, "Переданы некорректные данные")
               
        recipient_company_id = data.get("recipient_company_id")

        if not recipient_company_id:
            raise HTTPException(400, "Поле recipient_company_id пустое")

        if sender_company_id == recipient_company_id:
            raise HTTPException(400, "Компания не может быть партнером самой себе")

        try:
            client = await ConnMongo.connect_to_mongo()
            if client is None:
                raise HTTPException(500, "Не удалось подключиться к MongoDB")
            
            db_companies = client["companies"]
            companies_collection = db_companies["companies"]

            db_partnerships = client["partnerships"]
            partnerships_collection = db_partnerships["partnerships"]

            # Проверяем существует ли компания
            existing_recipient = await companies_collection.find_one({"_id": ObjectId(recipient_company_id)})
            if not existing_recipient:
                raise HTTPException(404, "Такой компании не существует")
            
            # Проверяем партнерство в обоих направлениях
            partnership_filter = {
                "$or": [
                    {"company_a": sender_company_id, "company_b": recipient_company_id},
                    {"company_a": recipient_company_id, "company_b": sender_company_id}
                ]
            }
            
            existing_partnership = await partnerships_collection.find_one(partnership_filter)
            
            if existing_partnership:
                if existing_partnership["status"] == "Неактивно":
                    await partnerships_collection.delete_one({"_id": existing_partnership["_id"]})
                    return {"msg": "Отправленная заявка удалена"}
                    # raise HTTPException(400, "Ваша заявка уже отправлена")
                elif existing_partnership["status"] == "Активно":
                    raise HTTPException(400, "Вы уже партнеры")
                else:
                    raise HTTPException(400, "Неизвестный статус партнерства")

            # Создаем новую заявку
            await partnerships_collection.insert_one({
                "company_a": sender_company_id,
                "company_b": recipient_company_id,
                "status": "Неактивно",
            })

            return {"message": "Заявка на партнерство отправлена"}
            
        except HTTPException:
            raise  # Просто пробрасываем дальше
        except Exception as e:
            raise HTTPException(500, "Internal server error")
        finally:
            if client:
                client.close() 