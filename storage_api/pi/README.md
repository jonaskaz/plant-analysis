# Raspberry Pi Image Uploading

Take a picture on the raspberry pi and uploads it to the storage API

Create an env file first:
```
echo 'STORAGE_URL=http://INSERT_URL/' > .env
```

Run using a cronjob:
```
0 * * * * cd path/to/plant_analysis/storage_api/pi && dir/to/venv/bin/python3 upload_image.py
```