from fastapi import FastAPI
from routes.user import user

app = FastAPI(
    title="EP-Helper API"
)

app.include_router(user)