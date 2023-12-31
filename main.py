from fastapi import FastAPI
from routes.user import user
from routes.results import result
from routes.medical_observation import medical_observation
from routes.authentication import auth
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes.download import download
app = FastAPI(title="EP-Helper API")

app.include_router(user)
app.include_router(result)
app.include_router(medical_observation)
app.include_router(auth)
app.include_router(download)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add CORS middleware to allow requests from all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # This allows requests from all origins, you may want to restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],  # You can specify the HTTP methods you want to allow
    allow_headers=["*"],  # You can specify the HTTP headers you want to allow
)
