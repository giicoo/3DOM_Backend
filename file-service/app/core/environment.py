import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '../../../.env')
load_dotenv(dotenv_path=dotenv_path, override=True)

API_VERSION = os.getenv("API_VERSION")
APP_NAME = os.getenv("APP_NAME")
MONGO_URI = os.getenv("MONGO_URI")
OLLAMA_URI = os.getenv("OLLAMA_URI")

