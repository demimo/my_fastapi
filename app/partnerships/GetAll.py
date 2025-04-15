from fastapi import HTTPException
from bson import ObjectId
from typing import List, Dict, Any

from app.config.Config import ConnMongo

class GetAll:

    @staticmethod
    async def get_all(auth: Dict[str, Any]) -> Dict[str, Any]:
        # Получаем данные из JWT
        current_company_id = auth["company_id"]

        try:
            # Подключаемся к MongoDB
            client = await ConnMongo.connect_to_mongo()
            if client is None:
                raise HTTPException(status_code=500, detail="Не удалось подключиться к MongoDB")

            db_partnerships = client["partnerships"]
            partnerships_collection = db_partnerships["partnerships"]

            db_companies = client["companies"]
            companies_collection = db_companies["companies"]

            # Ищем все активные партнерства, где текущая компания участвует
            partnerships_cursor = partnerships_collection.find({
                "$or": [
                    {"company_a": current_company_id, "status": "Активно"},
                    {"company_b": current_company_id, "status": "Активно"}
                ]
            })
            
            partnerships = await partnerships_cursor.to_list(length=None)

            if not partnerships:
                return {"message": "Партнеры не найдены"}

            # Собираем ID партнеров (исключая текущую компанию)
            partner_ids = []
            for partnership in partnerships:
                if partnership["company_a"] == current_company_id:
                    partner_ids.append(ObjectId(partnership["company_b"]))
                else:
                    partner_ids.append(ObjectId(partnership["company_a"]))

            # Получаем информацию о компаниях-партнерах
            companies_cursor = companies_collection.find({
                "_id": {"$in": partner_ids}
            })
            companies = await companies_cursor.to_list(length=None)

            # Формируем список партнеров
            partners_list = [
                {
                    "partner_id": str(company["_id"]),
                    "name": company["name"]
                }
                for company in companies
            ]

            return {
                "message": "Партнеры успешно найдены",
                "count": len(partners_list),
                "partners": partners_list
            }

        except HTTPException:
            raise  # Просто пробрасываем дальше
        except Exception as e:
            raise HTTPException(500, "Internal server error")
        finally:
            if client:
                client.close() 