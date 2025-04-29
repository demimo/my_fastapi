from fastapi import HTTPException, Request
from bson import ObjectId

from app.config.Config import ConnMongo

class InfoCompany:

    @staticmethod
    async def info(auth, request: Request):
        
        # Получаем данные из JWT
        current_company_id = auth["company_id"]

        # 1. ПАРСИНГ ВХОДНЫХ ДАННЫХ
        try:
            data = await request.json()
            company_id = data.get("_id", "").strip()
            
            if not company_id:
                raise HTTPException(status_code=400, detail="Нет ID")
                
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=400, detail="Некорректный формат данных")

        # 2. ВЫПОЛНЕНИЕ ПОИСКА В БАЗЕ ДАННЫХ
        try:
            # Подключаемся к MongoDB
            client = await ConnMongo.connect_to_mongo()
            if client is None:
                raise HTTPException(status_code=500, detail="Не удалось подключиться к MongoDB")

            companies_collection = client["companies"]["companies"]
            partnerships_collection = client["partnerships"]["partnerships"]

            # Получаем информацию о компании по ID
            info_company = await companies_collection.find_one(
                {"_id": ObjectId(company_id)}
            )

            if not info_company:
                return {"message": "Кампания не найдена"}
            
            # Преобразуем ObjectId в строку
            info_company["_id"] = str(info_company["_id"])
            
            # Проверяем статус партнерства
            info_partnerships = await partnerships_collection.find_one({
                "$or": [
                    {"company_a": ObjectId(current_company_id), "company_b": ObjectId(info_company["_id"]), "status": "Активно"},
                    {"company_a": ObjectId(info_company["_id"]), "company_b": ObjectId(current_company_id), "status": "Активно"},
                    {"company_a": ObjectId(current_company_id), "company_b": ObjectId(info_company["_id"]), "status": "Неактивно"},
                    {"company_a": ObjectId(info_company["_id"]), "company_b": ObjectId(current_company_id), "status": "Неактивно"},
                ]
            })
            
            # Преобразуем ObjectId в строки для партнерства, если оно найдено
            if info_partnerships:
                info_partnerships["_id"] = str(info_partnerships["_id"])
                info_partnerships["company_a"] = str(info_partnerships["company_a"])
                info_partnerships["company_b"] = str(info_partnerships["company_b"])

            return {
                "company": info_company,
                "partnerships": info_partnerships
            }

        except HTTPException:
            raise  # Просто пробрасываем дальше
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal server error")
        finally:
            if client:
                client.close()