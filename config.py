import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    load_dotenv()  
    PROPAGATE_EXCEPTIONS = True
    API_TITLE = "STORE CHATBOT MVP"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAI_API_KEY = "sk-proj-l7ggu7dVuFtajCLia24PT3BlbkFJl1qoGuXnYAm42Mb1sF3A"
    OPEN_API_URL_PREFIX = "/" 
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URL') or  os.getenv("DATABASE_URL","sqlite:///chat.db") 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.environ['OPENAI_API_KEY']
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    