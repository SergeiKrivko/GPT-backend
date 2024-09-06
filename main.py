from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.chats.router import router as chats_router
from src.messages.router import router as messages_router
from src.utils.config import VERSION


app = FastAPI(
    title='Nachert API',
    description='Asynchronous API for Nachert',
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
        'data': 'Nachert API',
        'detail': f'Visit /docs or /redoc for the full documentation.'
    }


@app.get('/readyz', tags=['Setup'])
async def get_readyz_handler():
    return {
        'data': 'Ready',
        'detail': 'API is ready.'
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
