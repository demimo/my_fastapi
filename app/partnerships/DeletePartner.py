from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from app.config.Config import ConnPostgresqlUser


class DeletePartner:


    @staticmethod
    async def delete(request: Request, auth):

        # Получаем из JWT company_id
        company_id = auth["company_id"]

        # Получаем данные с формы:
        data = await request.json()
        if not data:
            raise HTTPException(status_code=400, detail="Переданы некорректные данные")
        
        partner_id = data.get("company_id")

        async with ConnPostgresqlUser() as conn:
            async with conn.transaction():

                # Проверяем существование активного партнерства
                partnership = await conn.fetchrow(
                    '''SELECT id 
                    FROM company_partnerships 
                    WHERE status_partnerships = $1 
                    AND (
                        (sender_company_id = $2 AND recipient_company_id = $3)
                        OR 
                        (sender_company_id = $3 AND recipient_company_id = $2)
                    )''',
                    True, company_id, partner_id
                )

                if not partnership:
                    return JSONResponse(
                        content={"message": "Таких партнеров у вас нет", "partners": []},
                        status_code=200
                    )

                await conn.execute(
                    'DELETE FROM company_partnerships WHERE id = $1',
                    partnership['id']
                )
                return {"msg": "Партнер удален"}