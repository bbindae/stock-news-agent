import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

print(f"EnvPath:{ENV_PATH}")

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
    print(".env file loaded successfully")


