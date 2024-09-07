import os
import subprocess
import sys

import dotenv

dotenv.load_dotenv()

if sys.platform == 'win32':
    path = ".venv/Scripts"
else:
    path = ".venv/bin"

message = input('Enter migration name: ')

subprocess.run(f"{path}/alembic -c migrations/alembic.ini revision --message='{message}' --autogenerate")
