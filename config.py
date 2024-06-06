# This file contains the configuration settings for the Flask application.

from dotenv import load_dotenv 
import os

class Config:
    load_dotenv()  
    PROPAGATE_EXCEPTIONS = True
    API_TITLE = "STORE CHATBOT MVP"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAI_API_KEY = "sk-proj-l7ggu7dVuFtajCLia24PT3BlbkFJl1qoGuXnYAm42Mb1sF3A"
    OPEN_API_URL_PREFIX = "/"
    #OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"     
    #OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"  
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URL') or  os.getenv("DATABASE_URL","sqlite:///chat.db") 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.environ['OPENAI_API_KEY']
    MAX_QUESTIONS = 5

   