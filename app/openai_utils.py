import openai
from flask import current_app
import os
from openai import OpenAI

openai.api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI()

def get_initial_message(role, industry, situation, applicant_name, applicant_surname, language):
    return f""" 
    - You have to ask question first to {applicant_name} {applicant_surname} to start the interview for the {role} position in the {industry} industry.
    - The question must be asked in {language}. 
    - Start with a small presentation sentence of the job to welcome the candidate. 
    - The name of the candidate is {applicant_name} {applicant_surname}. 
    - Be polite, introduce the reason of the interview, i.e., remember him that the interview is about a {role} position in the {industry} industry. 
    - Then, ask the first question."""

def get_thank_you_message(applicant_name):
    return f"Thank you for the interview, {applicant_name}. We will keep you in touch as soon as possible."



def create_openai_thread(language, role, industry, situation, applicant_name, applicant_surname):
    
    openai_api_key = current_app.config.get('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
    
    client.api_key = openai_api_key
    instructions = (
        f"""
        - You are a HR that wants to interview an applicant whose name is {applicant_name} {applicant_surname}. 
        - Always finish your answer by a question to the applicant regarding the {role} and {industry}.
        - Be concise in your questions (not too much text per question).
        - Only discuss with him by calling him with his name ({applicant_name}). 
        - If the user's answer is not related to your question, please tell him to focus on the interview which is about the {role} and {industry}.
        - Ask questions in {language}. The whole conversation must be in  in {language}. 
        - If the applicant answer in another language, you have to tell him that the intevriew  is in {language} and that any other language's answer will not be considered. 
        - Only ask one question per message. Also, the subsequent messages must take into account the conversation thread as a natural conversation. 
        - Feel free to ask for examples or previous experiences of the applicant.
        - Feel also free to ask question that are more and more precise based on the applicant previous answers.
        - Ask for more details if the answer is not satisfying or if you think that the applicant can go more in details."""
    )
    
    # ASSISTANT CREATION 
    assistant = client.beta.assistants.create(
        name="Interview Thread",
        instructions=instructions,
        tools=[],
        model="gpt-3.5-turbo",
    )

    initial_message = get_initial_message(role, industry, situation, applicant_name, applicant_surname,language)

    # THREAD CREATION
    thread = client.beta.threads.create(
        messages = [
            {
                "role": "assistant",
                "content": initial_message
            }
        ]
    )
    # RUN THREAD
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id = assistant.id
    )

    run_status = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id = run.id
    )

    if run_status.status == "completed":
        messages = client.beta.threads.messages.list(
            thread_id = thread.id)

    #thread_id = response['id']
    thread_id = thread.id
    assistant_id = assistant.id

    # RETRIEVE MESSAGE
    first_message = messages.data[0].content[0].text.value
    return thread_id, assistant_id, first_message

def get_openai_thread_response(thread_id, assistant_id, user_message):
    openai_api_key = current_app.config.get('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
    
    #openai.api_key = openai_api_key

    user_response = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message,
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id = assistant_id
    )

    # Retrieve the curent status of the assistant's run
    run_status = client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id = run.id
    )
    
    # Check if the run status is completed and ask for an Assistant message
    if run_status.status == "completed":
        messages = client.beta.threads.messages.list(
            thread_id = thread_id)
    assistant_response = messages.data[0].content[0].text.value

    return assistant_response