from typing import List

import logging
import json

from fastapi import FastAPI, Security, Depends, HTTPException
from fastapi.security.api_key import APIKeyHeader, APIKey
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

from PIL import Image, ImageDraw, ImageFont

from secrets import api_key

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO

API_KEY = api_key
API_KEY_NAME = "access_token"

api_key_header = APIKeyHeader(name=API_KEY_NAME)

async def get_api_key(
    api_key_header: str = Security(api_key_header)
):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=403, detail="Could not validate API Key"
        )

class Task(BaseModel):
    name: str
    status: str

class TaskWrapper(BaseModel):
    tasks: List[Task]

@app.get('/', response_model=str)
def root():
    return "Nothing to see here."
    
@app.get('/tasks', response_model=dict)
async def get_tasks(api_key: APIKey = Depends(get_api_key)):
    logger.info(f"Reading tasks.")
    with open("db.json", "r+") as file:
        file_data = json.load(file)
        logger.info(file_data)
        return file_data

@app.put('/tasks', response_model=str)
async def put_tasks(data: TaskWrapper, api_key: APIKey = Depends(get_api_key)):
    logger.info(f"Received data.")

    json_data = jsonable_encoder(data)
    
    logger.info(f"Saving data.")
    with open("db.json", "w+") as file:
        file.seek(0)
        json.dump(json_data, file, indent=4)
        file.close()
        logger.info(f"Data saved.")

    logger.info(f"Generating image.")
    with Image.open('images/background.png').convert("RGBA") as img:
        draw = ImageDraw.Draw(img)

        ##### Replace "SF-Pro-Text-Medium.otf" with the filename of a font you choose to upload #####
        font = ImageFont.truetype("SF-Pro-Text-Medium.otf", 16)
        ##### ----- ----- ----- ----- ----- ----- --------- ----- ----- ----- ----- ----- ----- #####

        y = 109
        for item in json_data["tasks"]:
            if item["status"] == "open":
                cbox = Image.open('images/open_task.png').convert("RGBA")
            else:
                cbox = Image.open('images/complete_task.png').convert("RGBA")
            img.alpha_composite(cbox, dest=(72, y + 3))
            cbox.close()
            draw.text((100, y), item["name"], font=font, fill=(0, 0, 0, 255))
            y += 23
            if y > 384:
                break
        img = img.convert("RGB")
        img.save('static/current_tasks.jpg', "JPEG")
        img.close()
        logger.info(f"Image generated.")
    
    return ("Tasks processed.")
        
### DEBUG - Immediately generate image locally using placeholder tasks
# debug_task_open = Task(name = "Task", status = "open")
# debug_task_complete = Task(name = "Task", status = "completed")
# debug_task_wrapper = TaskWrapper(tasks = [debug_task_open, debug_task_complete])

# process = put_tasks(debug_task_wrapper)
# print(process)
    