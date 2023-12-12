from fastapi import FastAPI
from routes.user import user
from routes.authentication import auth
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="EP-Helper API"
)

app.include_router(user)
app.include_router(auth)

# Add CORS middleware to allow requests from all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows requests from all origins, you may want to restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],  # You can specify the HTTP methods you want to allow
    allow_headers=["*"],  # You can specify the HTTP headers you want to allow
)
