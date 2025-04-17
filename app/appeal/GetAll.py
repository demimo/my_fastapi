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

            db_appeals = client["appeals"]
            appeals_collection = db_appeals["appeals"]

            # Ищем все активные обращения, где текущая компания является ответственной
            appeal_cursor = appeals_collection.find({
                "responsible_company_id": current_company_id, 
                "status": {"$ne": "Закрыто"}  # Исправлен синтаксис условия
            })
            
            appeals = await appeal_cursor.to_list(length=None)

            if not appeals:
                return {"message": "Обращения не найдены"}

            # Формируем список обращений
            appeals_list = []
            for appeal in appeals:
                try:

                    # Обрабатываем participants согласно структуре
                    participants_data = appeal.get("participants", {})
                    participants = {
                        "company_ids": [str(cid) for cid in participants_data.get("company_id", [])],
                        "user_ids": [str(uid) for uid in participants_data.get("user_id", [])]
                    }

                    appeal_data = {
                        "_id": str(appeal.get("_id", "")),
                        "subject": appeal.get("subject", ""),
                        "status": appeal.get("status", ""),
                        "priority": appeal.get("priority", ""),
                        "creator_company_id": str(appeal.get("creator_company_id", "")),
                        "creator_user_id": str(appeal.get("creator_user_id", "")),
                        "responsible_company_id": str(appeal.get("responsible_company_id", "")),
                        "responsible_user_id": str(appeal.get("responsible_user_id", "")),
                        "participants": participants,  # Исправленная структура participants
                        "created_at": appeal.get("created_at", ""),
                        "updated_at": appeal.get("updated_at", ""),  
                    }
                    appeals_list.append(appeal_data)
                except Exception as e:
                    continue  # Пропускаем проблемные записи

            return {
                "message": "Обращения успешно найдены",
                "count": len(appeals_list),
                "appeals": appeals_list
            }


        except HTTPException:
            raise  # Просто пробрасываем дальше
        except Exception as e:
            raise HTTPException(500, "Internal server error")
        finally:
            if client:
                client.close() 