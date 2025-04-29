from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware

from app.user.logics.Registration import Registration
from app.user.logics.Login import Login
from app.user.logics.Check import Check
from app.user.logics.Logout import Logout
from app.user.logics.Device import Device
from app.user.logics.CreateUser import CreateUser
from app.user.logics.UpdateUser import UpdateUser
from app.user.logics.GetAll import GetAll as GetAllUsers

from app.partnerships.Sender import Sender
from app.partnerships.Recipient import Recipient
from app.partnerships.GetAll import GetAll as GetAllPartners
from app.partnerships.search.Search import Search
from app.partnerships.search.InfoCompany import InfoCompany


from app.appeal.Create import Create as CreateAppeal
from app.appeal.GetAll import GetAll as GetAllAppeal


app = FastAPI()

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем запросы от всех доменов
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы
    allow_headers=["*"],  # Разрешаем все заголовки
)


@app.post("/registration")
async def reg(request: Request, response: Response):
    data = await Registration.registration(request, response)
    return data

@app.post("/login")
async def log(request: Request, response: Response):
    data = await Login.login(request, response)
    return data

@app.get("/checkauth")
async def log(request: Request):
    data = await Check.check(request)
    return data

@app.post("/logout")
async def out(request: Request, response: Response):
    data = await Logout.logout(request, response)
    return data

@app.get("/device")
async def dev(request: Request):
    data = await Device.device(request)
    return data




@app.post("/create/user")
async def cre(request: Request):
    auth = await Check.check(request)
    data = await CreateUser.create(request, auth)
    return data

@app.post("/update/user")
async def upd(request: Request):
    auth = await Check.check(request)
    data = await UpdateUser.update_user(request, auth)
    return data

@app.get("/users/get/all")
async def rec(request: Request):
    auth = await Check.check(request)
    data = await GetAllUsers.get_all(auth)
    return data






@app.post("/company/search")
async def rec(request: Request):
    auth = await Check.check(request)
    data = await Search.search(auth, request)
    return data

@app.post("/company/search/info")
async def rec(request: Request):
    auth = await Check.check(request)
    data = await InfoCompany.info(auth, request)
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

@app.get("/get/all")
async def rec(request: Request):
    auth = await Check.check(request)
    data = await GetAllPartners.get_all(auth)
    return data







@app.post("/appeal/create")
async def rec(request: Request):
    auth = await Check.check(request)
    data = await CreateAppeal.create(request, auth)
    return data

@app.get("/appeals/get/all")
async def rec(request: Request):
    auth = await Check.check(request)
    data = await GetAllAppeal.get_all(auth)
    return data