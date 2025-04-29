from fastapi import HTTPException, Request
from app.config.Config import ConnMongo

class Search:
    @staticmethod
    async def search(auth, request: Request):
        """
        Поиск компаний по названию (частичному совпадению) или ИНН
        Возвращает список компаний (максимум 20) с id, названием и ИНН
        """
        
        # 1. ПАРСИНГ ВХОДНЫХ ДАННЫХ
        try:
            data = await request.json()
            company_name = data.get("name", "").strip()
            company_inn = data.get("inn", "").strip()
            
            if not company_name and not company_inn:
                raise HTTPException(400, "Нужно указать название компании или ИНН")
                
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(400, "Некорректный формат данных")

        # 2. ФОРМИРОВАНИЕ УСЛОВИЙ ПОИСКА
        search_filters = []
        
        if company_name:
            search_filters.append({
                "name": {
                    "$regex": f".*{company_name}.*",
                    "$options": "i"
                }
            })
        
        if company_inn:
            if company_inn.isdigit():
                try:
                    inn_number = int(company_inn)
                    search_filters.append({"inn": inn_number})
                except ValueError:
                    search_filters.append({
                        "inn": {
                            "$regex": f"^{company_inn}",
                            "$options": "i"
                        }
                    })
            else:
                search_filters.append({
                    "inn": {
                        "$regex": f"^{company_inn}",
                        "$options": "i"
                    }
                })

        # 3. ВЫПОЛНЕНИЕ ПОИСКА В БАЗЕ ДАННЫХ
        try:
            # Получаем клиент MongoDB (без async with)
            client = await ConnMongo.connect_to_mongo()
            if client is None:
                raise HTTPException(500, "Ошибка подключения к базе данных")
                
            companies_collection = client["companies"]["companies"]
            
            final_filter = {}
            if len(search_filters) == 1:
                final_filter = search_filters[0]
            else:
                final_filter = {"$or": search_filters}
            
            found_companies = await companies_collection.find(
                final_filter
            ).limit(20).to_list(length=20)
            
            # Закрываем подключение (если нужно)
            # client.close()  # Раскомментировать, если нужно явное закрытие
            
        except Exception as e:
            raise HTTPException(500, f"Ошибка при поиске в базе данных: {str(e)}")

        # 4. ФОРМИРОВАНИЕ РЕЗУЛЬТАТА
        if not found_companies:
            return {"message": "Компании не найдены"}
        
        result = []
        for company in found_companies:
            result.append({
                "_id": str(company["_id"]),
                "name": company.get("name", ""),
                "inn": company.get("inn", "")
            })
        
        return {"search": result}