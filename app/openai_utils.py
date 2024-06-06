import openai
from openai import OpenAI
from flask import current_app
import os

openai.api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI()

def create_openai_thread():
    openai_api_key = current_app.config.get('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "assistant",
                "content": "You have to ask question first to the user to start the interview for a job as CTO. "
                           "Start with a presentation sentence to welcome the candidate. The name of the candidate is Sidney. "
                           "Be polite and introduce the reason of the interview and remember him that the interview is about a "
                           "CTO position in an AI tech company. Then, ask the first question."
            }
        ]
    )
    return response.id, response.choices[0].message.content

def get_openai_thread_response(thread_id, user_message):
    openai_api_key = current_app.config.get('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content
