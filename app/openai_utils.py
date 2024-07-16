import openai
from flask import current_app
import os
from openai import OpenAI

openai.api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI()

def get_initial_message(role, industry, situation, applicant_name, applicant_surname, language):
    return f""" 
    - You are a helpful hiring assistant that has to conduct an interview.
    - You have to ask question first to {applicant_name} {applicant_surname} to start the interview for the {role} position in the {industry} industry.
    - The whole conversation is in {language}. 
    - Start with a small presentation sentence of the job to welcome the candidate. 
    - The name of the candidate is {applicant_name} {applicant_surname}. 
    - Then, ask the first question.
    - The first question should start a practical case study about {situation}. If there are multiple situations in {situation}, choose one of them.
    - If there is no situation in {situation}, you can imagine one practical case study for the {role} and {industry}.
    - Always start with a very precise practical case.  
    - You have to specify you case study with what should look like a real-life situation. 
    - Please tell the applicant which pratical case study you have chosen for the interview.
    - The first question should always be focused on the interview practical case scenario."""

def get_thank_you_message(applicant_name):
    return f"Thank you for the interview, {applicant_name}. We will keep you in touch as soon as possible!"



def create_openai_thread(language, role, industry, situation, applicant_name, applicant_surname):
    
    openai_api_key = current_app.config.get('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
    
    client.api_key = openai_api_key
    instructions = (
        f"""
        - You are a helpful hiring assistant aiming to interview an applicant whose name is {applicant_name} {applicant_surname}.
        - The interview must be conducted in {language}. If the applicant answer in another language, you have to tell him that the intevriew  is in {language} and that any other language's answer will not be considered. 
        - Always finish your answer by a question to the applicant.
        - The whole interview will be about a practical case study that you need to choose between one of the situation in {situation} regarding the {role} and {industry}.
        - If there are multiple situations in {situation}, only choose of them and conduct the whole interview about the chosen one.
        - Be concise in your questions (not too much text per question).
        - Be precise in your practical case questions.
        - Ask for the applicant's reasoning, chain of tought. 
        - The interview's language should be formal, concise, and practical. 
        - Only discuss with the applicant by calling him with his name {applicant_name}. 
        - If the user's answer is not related to your question, please tell him to focus on the interview which is about the {role} and {industry} about the practical case study.
        - Only ask one question per message. The subsequent messages must take into account the conversation thread as a natural conversation. 
        - Feel free to ask for examples or previous experiences of the applicant.
        - Feel also free to ask questions that are more and more precise based on the applicant previous answers. Bounce back on the applicant's answers.
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