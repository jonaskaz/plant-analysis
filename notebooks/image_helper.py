from datetime import datetime
import requests
import urllib.parse
import tempfile


class ImageHelper:
    def __init__(self, base_url: str):
        self.url = base_url + "files/"
        self.image = tempfile.NamedTemporaryFile(delete=False)

    def get(self, dt: datetime, im_type: str) -> bool:
        """
        Returns: true if image found, false otherwise
        """
        assert im_type in ["top", "side"]
        params = {"type": im_type}
        if dt:
            assert type(dt) == datetime
            params["dt"] = dt
        params = urllib.parse.urlencode(params)
        res = requests.get(self.url, params=params)
        if res.status_code != 200 or len(res.content) < 100:
            print(res.status_code)
            print(res.content)
            return False
        self.create_temp_image_file(res.content)
        return True

    def create_temp_image_file(self, image_bytes):
        self.image = tempfile.NamedTemporaryFile(delete=False)
        self.image.write(image_bytes)
        self.image.seek(0)

    def dt_from_string(self, dt_str: str) -> datetime:
        """
        dt_str: string of the format "day/month/year hour:minute:second"
        e.g. '01/04/2011 16:08:18'
        returns: datetime object
        """
        f = "%d/%m/%Y %H:%M:%S"
        return datetime.strptime(dt_str, f)
