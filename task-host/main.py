from typing import List

import logging
import json

from fastapi import FastAPI, Security, Depends, HTTPException
from fastapi.security.api_key import APIKeyHeader, APIKey
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from secrets import api_key
# Private module excluded by .gitignore
# def api_key() -> str:
#    return "API KEY GOES HERE"

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO

API_KEY = api_key()
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
        return "Data saved."
    