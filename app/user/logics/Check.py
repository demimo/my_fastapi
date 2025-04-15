from fastapi import Request, HTTPException
import datetime
from datetime import timezone


from app.user.func.CrudJwt import CrudJwt
from app.user.func.CrudRedis import CrudRedis


class Check:


    @staticmethod
    async def check(request: Request):

        # Получаем JWT из cookies
        jwt_token = request.cookies.get("sessionid")
        if not jwt_token:
            raise HTTPException(status_code=401, detail="Токена нет необходимо авторизоваться")

        # Получаем информацию из JWT
        payload = await CrudJwt.decode_token(jwt_token)
        user_id = payload.get("user_id")
        company_id = payload.get("company_id")
        role = payload.get("role")
        is_active = payload.get("is_active")
        device_id = payload.get("device_id")
        exp = payload.get("exp")

        # Проверяем корректность JWT
        if not user_id or not company_id or not role or not is_active or not device_id:
            raise HTTPException(status_code=401, detail="Отсутствует что из: user_id, company_id, role, is_active, device_id")

        # Преобразуем exp в datetime и сравниваем с текущим временем
        if datetime.datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Срок действия токена истек")

        # Получаем JWT с Redis
        data = await CrudRedis.get(user_id, device_id)
        if data != jwt_token:
            raise HTTPException(status_code=401, detail="Токена нет")

        return {
            "user_id": user_id,
            "company_id": company_id,
            "role": role,
            "is_active" : is_active,
        }
    

    @staticmethod
    async def check_for_logout(request: Request):
            
        # Получаем JWT из cookies
        jwt_token = request.cookies.get("sessionid")
        if not jwt_token:
            raise HTTPException(status_code=401, detail="Токен отсутствует")

        # Получаем информацию из JWT
        payload = await CrudJwt.decode_token(jwt_token)
        user_id = payload.get("user_id")
        device_id = payload.get("device_id")
        exp = payload.get("exp")
        # Проверяем, что user_id и device_id не пустые и exp не истек
        if not user_id or not device_id:
            raise HTTPException(status_code=401, detail="Неверный токен: отсутствует user_id или device_id")

        # Преобразуем exp в datetime и сравниваем с текущим временем
        if datetime.datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Срок действия токена истек")

        # Получаем JWT с Redis
        data = await CrudRedis.get(user_id, device_id)
        if data != jwt_token:
            raise HTTPException(status_code=401, detail="Токена нет")

        return user_id, device_id
    

    @staticmethod
    async def check_for_device(request: Request):
            
        # Получаем JWT из cookies
        jwt_token = request.cookies.get("sessionid")
        if not jwt_token:
            raise HTTPException(status_code=401, detail="Токен отсутствует")

        # Получаем информацию из JWT
        payload = await CrudJwt.decode_token(jwt_token)
        user_id = payload.get("user_id")
        device_id = payload.get("device_id")
        exp = payload.get("exp")
        # Проверяем, что user_id и device_id не пустые и exp не истек
        if not user_id or not device_id:
            raise HTTPException(status_code=401, detail="Неверный токен: отсутствует user_id или device_id")

        # Преобразуем exp в datetime и сравниваем с текущим временем
        if datetime.datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Срок действия токена истек")

        # Получаем JWT с Redis
        data = await CrudRedis.get(user_id, device_id)
        if data != jwt_token:
            raise HTTPException(status_code=401, detail="Токена нет")

        return user_id