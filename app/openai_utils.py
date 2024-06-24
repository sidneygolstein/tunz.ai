import openai
from flask import current_app
import os
from openai import OpenAI

openai.api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI()

def get_initial_message(role, industry, applicant_email):
    return f" You have to ask question first to {applicant_email} to start the interview for the {role} position in the {industry} industry. Start with a presentation sentence of the job to welcome the candidate. The name of the candidate is {applicant_email}. Be polite and introduce the reason of the interview and remember him that the interview is about a {role} position in the {industry} industry. Then, ask the first question."

def get_thank_you_message(applicant_email):
    return f"Thank you for the interview, {applicant_email}. We will keep you in touch as soon as possible."



def create_openai_thread(language, role, industry, applicant_email):
    
    openai_api_key = current_app.config.get('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
    
    client.api_key = openai_api_key


    instructions = (
        f"You are a HR that wants to interview an applicant. Always finish your answer by a question to the applicant please. Ask questions in {language}. The applicant must answer in {language}"
        if language == 'english'
        else f"Vous êtes un responsable des ressources humaines qui souhaite interviewer un candidat. Terminez toujours votre réponse par une question au candidat s'il vous plaît. Posez les questions en {language}. Le candidat doit répondre en {language}"
    )
    
    # ASSISTANT CREATION 
    assistant = client.beta.assistants.create(
        name="Test thread",
        instructions=instructions,
        tools=[],
        model="gpt-3.5-turbo",
    )

    initial_message = get_initial_message(role, industry, applicant_email)
    

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
