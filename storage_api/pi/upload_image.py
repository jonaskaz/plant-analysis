from picamera import PiCamera
from datetime import datetime

"""
Connect to camera
Take a picture
Save picture locally
Send the picture via API request to a url
"""


def format_time(dt):
    return dt.strftime("%Y.%m.%d.%H")


def dt_str():
    return format_time(datetime.now())


if __name__ == "__main__":

    camera = PiCamera()

    save_path = "./images/" + dt_str()

    camera.capture(save_path)
