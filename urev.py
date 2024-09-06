import os
import subprocess
import sys

import dotenv

dotenv.load_dotenv()

if sys.platform == 'win32':
    path = ".venv/Scripts"
else:
    path = ".venv/bin"

subprocess.run(f"{path}/alembic -c migrations/alembic.ini upgrade head")
