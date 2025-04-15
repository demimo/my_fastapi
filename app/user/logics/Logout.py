from fastapi import Request, Response


from app.user.logics.Check import Check
from app.user.func.CrudRedis import CrudRedis




class Logout:

    @staticmethod
    async def logout(request: Request, response: Response):

        # Проверяем авторизацию
        user_id, device_id = await Check.check_for_logout(request)
        
        # Удаляем запись из Redis
        await CrudRedis.delete(user_id, device_id)

        # Удаляем sessionid из cookies
        response.delete_cookie(key="sessionid")

        return {"msg": "Перенаправлен на страницу входа"}

