from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from datetime import datetime
import aiofiles
from pathlib import Path
import os

app = FastAPI()

side_image_save_dir = "./images/side/"
top_image_save_dir = "./images/top/"


def format_time(dt):
    return dt.strftime("%Y.%m.%d.%H")


def dt_str():
    return format_time(datetime.utcnow())


@app.on_event("startup")
async def startup_event():
    if not os.path.exists(side_image_save_dir):
        os.makedirs(side_image_save_dir)
    if not os.path.exists(top_image_save_dir):
        os.makedirs(top_image_save_dir)


@app.get("/")
async def root():
    return {"message": "Plantz!"}


@app.post("/uploadfile/")
async def create_upload_file(
    type: str,
    in_file: UploadFile = File(description="File description"),
):
    out_file_name = dt_str() + ".png"
    if type == "side":
        out_file_path = side_image_save_dir + out_file_name
    elif type == "top":
        out_file_path = top_image_save_dir + out_file_name
    async with aiofiles.open(out_file_path, "wb") as out_file:
        while content := await in_file.read(1024):  # async read chunk
            await out_file.write(content)  # async write chunk
    return {"filename": out_file_name}


@app.get("/files/")
async def get_file(dt: datetime | None = None, type: str = "top"):
    if not dt:
        dt = datetime.utcnow()
    if type == "top":
        filepath = top_image_save_dir + format_time(dt) + ".png"
    elif type == "side":
        filepath = side_image_save_dir + format_time(dt) + ".png"
    my_file = Path(filepath)
    if not my_file.is_file():
        return HTTPException(status_code=404, detail=f"Image {filepath} not found")
    return FileResponse(filepath)
