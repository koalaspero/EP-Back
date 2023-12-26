from fastapi.responses import FileResponse
from fastapi import APIRouter, HTTPException

download = APIRouter()


@download.get("/static/{file_name}")
async def download_file(file_name: str):
    file_path = f"static/{file_name}"
    return FileResponse(file_path)
