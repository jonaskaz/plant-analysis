import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO


load_dotenv()

base_url = os.environ.get("STORAGE_URL")


def post_image():
    url = base_url + "uploadfile/"
    files = {"in_file": open("./images/test.png", "rb")}
    res = requests.post(url, files=files)
    print(res.content)


def get_image():
    url = base_url + "files/"
    params = {"dt": datetime.utcnow()}
    res = requests.get(url, params=params)
    img = Image.open(BytesIO(res.content))
    img.show()


if __name__ == "__main__":
    #post_image()
    get_image()
