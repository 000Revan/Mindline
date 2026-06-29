from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from routers import users

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


origins = [
    "http://localhost",
    "http://localhost:5173",
    "https://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      #允许的源，开发阶段允许所有源，生产环境需要指定源
    allow_credentials=True,     #允许携带cookie
    allow_methods=["*"],        #允许的请求方法
    allow_headers=["*"],        #允许的请求头
)

# 挂载路由
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
