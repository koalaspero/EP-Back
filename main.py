from fastapi import FastAPI
from routes.user import user
from routes.authentication import auth
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="EP-Helper API"
)

app.include_router(user)
app.include_router(auth)

# Allow all origins in development, replace "*" with your production frontend URL
origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)