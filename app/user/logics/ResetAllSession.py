from app.user.func.CrudRedis import CrudRedis

class ResetAllSession:

    @staticmethod
    async def reset(user_id):
        
        # Удаляем запись из Redis
        delete = await CrudRedis.deleteAll(user_id)
        if delete:
            return {"msg": "Все сессии пользователя удалены"}