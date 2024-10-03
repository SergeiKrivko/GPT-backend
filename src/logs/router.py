from datetime import datetime

from fastapi import APIRouter

from src.logs.schemas import LogRead
from src.utils.dependency import FirebaseDep
from src.utils.exceptions import exception_handler

router = APIRouter(prefix='/logs', tags=['Logs'])


@router.post('/')
@exception_handler
async def get_models_handler(data: LogRead, firebase_client: FirebaseDep):
    await firebase_client.upload_text_file(f"logs/{data.application}/{data.version}/{datetime.now()}.txt", data.log)
