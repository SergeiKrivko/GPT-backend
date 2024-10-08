import sys
from datetime import datetime

import socketio
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from loguru import logger

from src.chats.router import router as chats_router
from src.messages.router import router as messages_router
from src.gpt.router import router as gpt_router
from src.translate.router import router as translate_router
from src.releases.router import router as releases_router
from src.logs.router import router as logs_router
from src.utils.config import VERSION
from src.sockets.manager import sio
from src.sockets.router import init as socket_init

app = FastAPI(
    title='GPT-chat API',
    description='Asynchronous API for GPT-chat',
    version=VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        '*'
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@app.get(f'/', tags=['Setup'])
async def get_root_handler():
    return {
        'data': 'GPT-chat API',
        'detail': f'Visit /docs or /redoc for the full documentation.'
    }


@app.get('/readyz', tags=['Setup'])
async def get_readyz_handler():
    return {
        'data': 'Ready',
        'detail': 'API is ready.'
    }


@app.get('/time', tags=['Setup'])
async def get_time_handler():
    return {
        'data': datetime.now(),
        'detail': 'Server time was selected.'
    }


@app.get('/healthz', tags=['Setup'])
async def get_healthz_handler():
    return {
        'data': 'Health',
        'detail': 'API is healthy.'
    }


@app.get('/publication/ready', tags=['Setup'])
async def get_publication_ready_handler():
    return {
        'data': 'Ready',
        'detail': 'API is ready to be published.'
    }


@app.get('/api/v1/version', tags=['Setup'])
async def get_version_handler():
    return {
        'data': VERSION,
        'detail': 'Version was selected.'
    }


app.include_router(chats_router, prefix='/api/v1')
app.include_router(messages_router, prefix='/api/v1')
app.include_router(gpt_router, prefix='/api/v1')
app.include_router(translate_router, prefix='/api/v1')
app.include_router(releases_router, prefix='/api/v1')
app.include_router(logs_router, prefix='/api/v1')

socket_init()

app = socketio.ASGIApp(sio, app)

# logger.add(sys.stdout, colorize=True, format="<level>{level}:</level> {message}", level="INFO")
