import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    APP_NAME = os.getenv("APP_NAME", "Bitespeed Identity Service")
