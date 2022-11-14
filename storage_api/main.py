from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from datetime import datetime
import aiofiles
from pathlib import Path
import os

app = FastAPI()

image_save_dir = "./images/"


def format_time(dt):
    return dt.strftime("%Y.%m.%d.%H")


def dt_str():
    return format_time(datetime.now())


@app.on_event("startup")
async def startup_event():
    if not os.path.exists(image_save_dir):
        os.makedirs(image_save_dir)


@app.get("/")
async def root():
    return {"message": "Plantz!"}


@app.post("/uploadfile/")
async def create_upload_file(
    in_file: UploadFile = File(description="File description"),
):
    out_file_name = dt_str() + ".png"
    out_file_path = image_save_dir + out_file_name
    async with aiofiles.open(out_file_path, "wb") as out_file:
        while content := await in_file.read(1024):  # async read chunk
            await out_file.write(content)  # async write chunk
    return {"filename": out_file_name}


@app.get("/files/")
async def get_file(dt: datetime | None = None):
    if not dt:
        dt = datetime.now()
    filepath = image_save_dir + format_time(dt) + ".png"
    my_file = Path(filepath)
    if not my_file.is_file():
        return HTTPException(status_code=404, detail=f"Image {filepath} not found")
    return FileResponse(filepath)
