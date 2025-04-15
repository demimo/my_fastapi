from fastapi import Request


from app.user.logics.Check import Check
from app.user.func.CrudRedis import CrudRedis




class Device:

    @staticmethod
    async def device(request: Request):

        # Проверяем авторизацию
        user_id = await Check.check_for_device(request)

        # Выводим все устройства
        all_info_device = await CrudRedis.getAll(user_id)

        return all_info_device

