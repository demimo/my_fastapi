pip install "fastapi[standard]"
uvicorn app.main:app --reload


pip install asyncpg
pip install python-dotenv
pip install redis
pip install PyJWT


docker build -t my_fastapi_app .
docker run -d --name appeal -p 80:80 my_fastapi_app
