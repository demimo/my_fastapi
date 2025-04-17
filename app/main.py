from fastapi import FastAPI, Response, Request

# from app.config.InitCompany import InitCompany
# from app.config.InitUser import InitUser
# from app.config.InitAppeal import InitAppeal

from app.user.logics.Registration import Registration
from app.user.logics.Login import Login
from app.user.logics.Check import Check
from app.user.logics.Logout import Logout
from app.user.logics.Device import Device
from app.user.logics.CreateUser import CreateUser
from app.user.logics.UpdateUser import UpdateUser

from app.partnerships.Sender import Sender
from app.partnerships.Recipient import Recipient
from app.partnerships.GetAll import GetAll as GetAllPartners


from app.appeal.Create import Create as CreateAppeal
from app.appeal.GetAll import GetAll as GetAllAppeal


app = FastAPI()


# @app.get("/initpg")
# async def startup_event():
#     await InitCompany.initialize_tables()
#     await InitUser.initialize_tables()
#     await InitAppeal.initialize_tables()
#     print("🚀 Приложение запущено, таблицы инициализированы, добавлены тестовые данные.")




@app.post("/registration")
async def reg(request: Request, response: Response):
    data = await Registration.registration(request, response)
    return data

@app.post("/login")
async def log(request: Request, response: Response):
    data = await Login.login(request, response)
    return data

@app.post("/logout")
async def out(request: Request, response: Response):
    data = await Logout.logout(request, response)
    return data

@app.get("/device")
async def dev(request: Request):
    data = await Device.device(request)
    return data




@app.post("/createuser")
async def cre(request: Request):
    auth = await Check.check(request)
    data = await CreateUser.create(request, auth)
    return data

@app.post("/updateuser")
async def upd(request: Request):
    auth = await Check.check(request)
    data = await UpdateUser.update_user(request, auth)
    return data








@app.post("/sender")
async def sen(request: Request):
    auth = await Check.check(request)
    data = await Sender.sender(request, auth)
    return data

@app.post("/recipient")
async def rec(request: Request):
    auth = await Check.check(request)
    data = await Recipient.recipient(request, auth)
    return data

@app.get("/getall")
async def rec(request: Request):
    auth = await Check.check(request)
    data = await GetAllPartners.get_all(auth)
    return data





@app.post("/appeal/create")
async def rec(request: Request):
    auth = await Check.check(request)
    data = await CreateAppeal.create(request, auth)
    return data

@app.get("/appeal/get/all")
async def rec(request: Request):
    auth = await Check.check(request)
    data = await GetAllAppeal.get_all(auth)
    return data




# @app.post("/invitepartner")
# async def created(request: Request):
#     auth = await Check.check(request)
#     data = await InvitePartner.invite(request, auth)
#     return data

# @app.post("/answerpartner")
# async def created(request: Request):
#     auth = await Check.check(request)
#     data = await AnswerPartner.answer(request, auth)
#     return data

# @app.get("/getallpartner")
# async def created(request: Request):
#     auth = await Check.check(request)
#     data = await GetAllPartners.get_all(auth)
#     return data

# @app.post("/deletepartner")
# async def created(request: Request):
#     auth = await Check.check(request)
#     data = await DeletePartner.delete(request, auth)
#     return data














    
# @app.post("/createdappeal")
# async def created(request: Request):
#     auth = await Check.check(request)
#     data = await Create.create(request, auth)
#     return data

# @app.post("/closedappeal")
# async def created(request: Request):
#     auth = await Check.check(request)
#     data = await Close.close(request, auth)
#     return data

# @app.get("/getallappeals")
# async def created(request: Request):
#     auth = await Check.check(request)
#     data = await GetAll.get_all(auth)
#     return data

# @app.get("/getamydirectorappeals")
# async def created(request: Request):
#     auth = await Check.check(request)
#     data = await GetMyDirector.get_my_director(auth)
#     return data

# @app.get("/getamyexecutorappeals")
# async def created(request: Request):
#     auth = await Check.check(request)
#     data = await GetMyExecutor.get_my_executor(auth)
#     return data



