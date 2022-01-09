from typing import Optional
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.staticfiles import StaticFiles
import pyminizip
import urllib.request
import os
import time

app = FastAPI()
app.mount("/files", StaticFiles(directory="files"), name="files")


def prepare_file(url: str, destination: str, archive_name: str):
    # Скачивание файла
    local_filename, headers = urllib.request.urlretrieve(url, destination)

    # Добавление файла в архив с паролем
    password = "12345"
    # compress level
    com_lvl = 5
    # compressing file
    pyminizip.compress(local_filename, None, archive_name, password, com_lvl)


def delete_files(destination: str, archive_name: str):
    time.sleep(120)
    os.remove(destination)
    os.remove(archive_name)


def get_destination_file_path(url):
    return f"files/{url.rsplit('/', 1)[1]}"


def get_archive_file_path(destination):
    return f"{destination}.zip"


def get_archive_file_name(archive_file_path):
    return archive_file_path.rsplit('/', 1)[1]


@app.get("/get-file/")
def get_file(request: Request, background_tasks: BackgroundTasks, url: Optional[str] = None):
    if url:
        destination = get_destination_file_path(url)
        archive = get_archive_file_path(destination)

        background_tasks.add_task(prepare_file, url, destination, archive)
        background_tasks.add_task(delete_files, destination, archive)

        file_url = (request.url_for('files', path=get_archive_file_name(archive)))
        return {"original_url": url, "new_file": file_url}

    return {"original_url": url, "new_url": ""}
