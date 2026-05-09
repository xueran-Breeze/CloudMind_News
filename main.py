from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import news, users, favorite, history, ai_chat
from utils.exception_handler import register_exception_handler

app = FastAPI()

# 注册异常处理器
register_exception_handler(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 允许的源
    allow_credentials=True, # 允许携带Cookie
    allow_methods=["*"], # 允许的方法
    allow_headers=["*"], # 允许的头
)

@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)
app.include_router(ai_chat.router)