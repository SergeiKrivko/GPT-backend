import os

VERSION = '0.0.1'

FIREBASE_SA_KEY = os.getenv('FIREBASE_SA_KEY')

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

OCR_API_KEY = os.getenv('OCR_API_KEY')
