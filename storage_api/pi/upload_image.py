from datetime import datetime
import requests
import os
from dotenv import load_dotenv


load_dotenv()

base_url = os.environ.get("STORAGE_URL")


def format_time(dt):
    return dt.strftime("%Y.%m.%d.%H")


def dt_str():
    return format_time(datetime.utcnow())


def capture(save_path):
    os.system(
        f"raspistill -o {save_path}",
    )


def upload(save_path):
    url = base_url + "uploadfile/"
    files = {"in_file": open(save_path, "rb")}
    return requests.post(url, files=files)


def run():
    save_path = "./images/" + dt_str() + ".jpeg"
    capture(save_path)
    print(f"Saved {save_path}")
    upload(save_path)
    print(f"Uploaded {save_path}")


if __name__ == "__main__":
    run()
