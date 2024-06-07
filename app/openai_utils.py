import openai
from flask import current_app
import os
from openai import OpenAI

openai.api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI()

def create_openai_thread():
    
    openai_api_key = current_app.config.get('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
    
    client.api_key = openai_api_key

    
    # ASSISTANT CREATION 
    assistant = client.beta.assistants.create(
        name="Test thread",
        instructions="You are a HR that wants to interview an applicant. Always finsih your anwer by a question to the applicant please.",
        tools=[],
        model="gpt-3.5-turbo",
    )


    # THREAD CREATION
    thread = client.beta.threads.create(
        messages = [
            {
                "role": "assistant",
                "content": "You have to ask question first to the user to start the interview for a job as CTO. \
                Start with a presentation sentence to welcome the candidate. The name of the candidate is Sidney. \
                Be polite and introduce the reason of the interview and remember him that the intervoew is about a \
                CTO position in a AI tech company.Then, ask the first question."
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
