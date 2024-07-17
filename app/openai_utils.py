import openai
from flask import current_app
import os
from openai import OpenAI
import json 

openai.api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI()

def get_initial_message(role, industry, situation, applicant_name, applicant_surname, language, company_name):
    return f""" 
    - You are an assistant expert in the field of recruiting and hiring, especially for the {role} and {industry}.
    - You have been mandated by the company {company_name} to help them hire the best and most talented candidates for the {role} role.
    - Your objective is to interview an applicant whose name is {applicant_name} {applicant_surname} and ensure the company only hires the best talent.
    - You have to ask a first question to {applicant_name} {applicant_surname} to start the interview for the {role} position in the {industry} industry.
    - The whole conversation is in {language}. 
    - Start with a small (very concise) presentation sentence of the {role} position in the {industry} to welcome the candidate. Also mention to the applicant that the interview will be centered around real-life situational-based interview questions to test their skills in practical situations.
    - The name of the candidate is {applicant_name} {applicant_surname}. 
    - Then, ask the first question.
    - The first question should start with a practical situational-based question relevant for the following situation: {situation}, role: {role} and industry: {industry} . If there are multiple situations in {situation}, choose one of them.
    - If there is no situation in {situation}, you can generate one practical situational-based interview question that is the most relevant for the the role: {role} and the industry: {industry}.
    - Always start with a precise situational-based interview question that is simulating a real-life business / professional situation (or scenario) that is the most relevant for the situation: {situation}, the role: {role} and the industry: {industry}
    - The first question should always be focused on the interview situational-based interview question scenario.
    - Please be as concise as possible to ensure the initial message and question are not too long.
    """

def get_thank_you_message(applicant_name):
    return f"Thank you for the interview, {applicant_name}. We will keep you in touch as soon as possible!"



def create_openai_thread(language, role, industry, situation, applicant_name, applicant_surname, company_name):
    
    openai_api_key = current_app.config.get('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
    
    client.api_key = openai_api_key
    instructions = (
        f"""
        - You are an assistant expert in the field of recruiting and hiring, especially for the {role} and {industry}.
        - You have been mandated by the company {company_name} to help them hire the best and most talented candidates for the {role} role.
        - Your objective is to interview an applicant whose name is {applicant_name} {applicant_surname} and ensure the company only hires the best talent.
        - Your guidelines for the interview are as follows:
        - The interview must be conducted in {language}. If the applicant answers in another language, you have to tell him that the interview  is in {language} and that any other language's answer will not be considered. 
        - The interview must be centered around asking applicants a role (for the following role: {role}) and industry (for the following industry: {industry}) specific situational-based interview questions (situational-based interview questions are an effective way to assess a candidate's problem-solving skills, communication skills, creativity skills, decision-making abilities, and leadership qualities in practical situations. By presenting candidates with real-life scenarios, you can gauge amongst others, their critical thinking, communication, and conflict-resolution skills. Because every industry and role has a unique set of challenges and opportunities, employers assess how well candidates are prepared to manage these circumstances before they make a hiring decision. Situational-based interview questions focus on how you'll handle (hypothetical) real-life scenarios you may encounter in the workplace and how you've handled similar situations in previous roles. Asking these questions will help the company better understand the applicant's thought process, problem-solving, self-management and communication skills).
        - To ensure to ask the applicant the most relevant situational-based interview question for the {role} and {industry}, please generate new specific situational-based interview questions based on one of the situation in {situation} regarding the {role} and {industry}.
        - Each situational-based question should be very specific, using the company name {company_name} and industry {industry} to ensure the question is as relevant as possible for the applicant and company.
        - Each situational-based question should be presented and explained like a very short and concise case interview where you lay out some very short and concise context and a situational-based question that mimics a real-life scenario to understand what an applicant would do in each situation and how they think about the problem and how to solve it.
        - If there are multiple situations in {situation}, only choose one of them and conduct the whole interview about this chosen situation. 
        - If there is no situation in {situation}, generate situational-based interview questions around a situation you think is the most relevant for the specific {role} and {industry}.
        - Be concise in your questions (not too much text per question).
        - Be precise in your practical situational-based interview questions.
        - Don’t ask closed-ended questions where the applicant can respond using only “yes” or “no”, instead ask open-ended questions to ensure you capture the applicant's reasoning and chain of thought.
        - Ask for the applicant's reasoning, chain of thought. 
        - The interview's language should be formal, concise, and practical. 
        - Only discuss with the applicant by calling him with his name {applicant_name}. 
        - If the user's answer is not related to your question, please tell him to focus on the interview which is about the {role} and {industry} about the practical situational-based interview.
        - Only ask one question per message. The subsequent messages must take into account the conversation thread as a natural conversation. 
        - After an applicant's answer, please ask clarifying questions about the applicant’s answer if the answer is not specific, relevant or concrete enough.
        - After an applicant's answer, please deep dive into specific parts of his answer and ask follow-up drill down questions to go deeper to understand in more detail the applicant’s reasoning and answers or to ask for potential next steps, bouncing back on the applicant's answers.
        - The entire thread should feel like a normal conversation for the candidate, very natural and engaging, making sure that any non relevant, weak or too short answer is questioned about and making sure that good, structured, logical and concise answers are deep-dived on to get more details from the candidates

    """
    )
    
    # ASSISTANT CREATION 
    assistant = client.beta.assistants.create(
        name="Interview Thread",
        instructions=instructions,
        tools=[],
        model="gpt-3.5-turbo",
    )

    initial_message = get_initial_message(role, industry, situation, applicant_name, applicant_surname,language, company_name)

    # THREAD CREATION

    ### CHANGE TO GET INITIAL MESSAGE

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









def create_scoring_thread(language, role, industry, situation, conversation):
    
    openai_api_key = current_app.config.get('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
    
    client.api_key = openai_api_key
    instructions = (
        f"""
            - You are an helpful assistant expert in field hiring candidates for {role} in the {industry} industry
            - Your objective is to review the quality of the interview of the applicant. 
            - The interview is stored in {conversation} (it's a set of questions/answers) 
            - The questions are the questions asked by the interviewer
            - The answers are the answers of the assistant based on the interviewer's questions. 
            - The evaluation is based on 6 evaluation criteria: 
                    - communication skills, 
                    - logical reasoning, structure and problem solving, 
                    - creativity, 
                    - business acumen, 
                    - analytical skills, 
                    - project management and prioritization.
            - The result of the evaluation should be a dictionary in a Json file (without spacing or breakline) with the 6 keys being the criteria (string) and the 6 corresponding values being a score (integer) from 0 to 10 based on their performance on each criteria. 
            - An example could be: f'{{"communication_skills":8,"logical_reasoning_and_structure_and_problem_solving":9,"creativity":6,"business_acumen":8,"analytical_skills":7,"project_management_and_prioritization":7}}
            - No spacing, no brackets, no brakes, no backslashes characters in the resulting dictionary please.
            - The values (ie. performance scores per criteria) are to be between 0 and 10 (0 being not relevant or extremely wrong/bad answer and 10 being an absolutely perfect answer/performance or score).
            - To assess the applicants responses and score the performance as a value  on a scale between 0 and 10 per criteria, please use the following guidelines of what a great / perfect scores looks like (ie. what very good looks like in applicant’s responses) per criteria: 
            - communication skills: The applicant is able to communicate and organize his answers clearly and concisely. He uses the pyramid principle to communicate effectively (The pyramid principle is a communication framework that employs an inverted pyramid technique. This tool is used for structuring the information and making a persuasive argument if you want to hold the audience’s attention and compellingly deliver your message. The basic idea of the pyramid principle is to get straight to the point in all written communications. The objective is to always start with the key point or conclusion / insight and then follow it by the rationale or arguments / data / facts supporting this conclusion or insight). The applicant must demonstrate the ability to summarize / synthesize his answers to provide short but complete and impactful answers.
            - logical reasoning, structure and problem solving: The applicant needs to be able to use logically constructed arguments & to structure thinking into clear and logical steps, using facts or data points to back up his arguments or to emphasize his points. It is important that a applicant demonstrates the ability to break up a bigger problem into smaller parts and analyze each part to find the root of the problem. applicants must as much as possible follow a MECE structure/framework (MECE is an acronym for the phrase Mutually Exclusive, Collectively Exhaustive. Put simply, it is a principle that will help you sharpen your thinking and simplify complex ideas into something that can be easily understood. MECE is made up of two parts. First, “mutually exclusive” is a concept from probability theory that says two events cannot occur simultaneously. For example, if you roll a six-sided die, the outcomes of a six or a three are mutually exclusive. When applied to information, mutually exclusive ideas would be distinctly separate and not overlapping. Second, “collectively exhaustive” means that the set of ideas includes all possible options. Going back to the six-sided dice example, the set {1,2,3,4,5,6} is mutually exclusive AND collectively exhaustive.), and demonstrate the ability to identify problems, isolate causes, and prioritize issues. If presented with data the applicant needs to demonstrate the ability to use this data to make recommendations and to construct a logical argumentation without rushing to conclusions based on insufficient evidence.
            - creativity: The applicant needs to demonstrate creativity when presented with a (business) question to be able to come up with innovative yet realistic examples to support his answer or find solutions to presented problems. The applicant needs to demonstrate the applicant's ability to think creatively and generate new ideas in response to complex challenges, listing multiple potential ideas. For marketing related roles, the candidate should show a great ability to understand customer behaviour, feeling and concepts around product branding and positioning.
            - business acumen: The applicant demonstrates a good understanding of relevant specific business situations, good business acumen demonstration and show a familiarity with various aspects of the business world (ie. business knowledge). Business acumen refers to the ability to make quick and accurate judgments or decisions in a business context based on experience, knowledge, and gut instincts. It is often described as a sense or feeling that guides individuals in understanding complex situations, anticipating outcomes, and identifying opportunities or risks. Business acumen is developed through a combination of expertise, observation, and pattern recognition. It involves drawing upon past experiences, industry knowledge, and a deep understanding of business dynamics to make informed judgments without relying solely on data or formal analysis. Business knowledge encompasses a range of concepts, principles, practices, and information related to different functional areas within an organization, industry dynamics, market trends, economic factors, and strategic decision-making processes. This type of knowledge can come from different sources such as business school, experience or industry certifications and covers many topics related to business success including marketing, finance, accounting, human resources, business strategies, leadership, operating, and many others.
            - analytical skills: The applicant must demonstrate the ability to collect data, break down problems, weigh up advantages and disadvantages, reach logical conclusions, understand and analyze data to uncover insights. applicants with these skills help companies spot difficult situations before they turn into problems (e.g. showing analytical prowess by deciphering graphs, charts, etc. to derive insights). Good applicants will formulate hypotheses to validate using data  in order to solve problems or uncover key insights, this requires working with numbers, interpreting data, and drawing meaningful conclusions that inform the overall strategy.
            - project management and prioritization: The applicant must demonstrate the ability to manage complex projects with conflicting deadlines, tasks and people’s agenda. A good applicant will be able to easily explain how he/she prioritizes tasks (e.g. using an important vs. urgent framework), what steps they would take to structure and set up a project planning & tracking plan for complex projects (and using examples from past projects to highlight key points), what tools are best fit to manage and track complex projects, how they can manage high time pressure and how to handle conflicting agenda’s at senior leadership level.
    """
    )
    
    # ASSISTANT CREATION 
    assistant = client.beta.assistants.create(
        name="Scoring Thread",
        model="gpt-3.5-turbo",
    )

    conversation_json = json.dumps(conversation)

    thread = client.beta.threads.create(
        messages = [
            {
                "role": "user",
                "content": conversation_json
            }
        ]
    )
    # RUN THREAD
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id = assistant.id,
        model="gpt-3.5-turbo",
        instructions = instructions,
    )

    run_status = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id = run.id
    )

    if run_status.status == "completed":
        messages = client.beta.threads.messages.list(
            thread_id = thread.id)

    # RETRIEVE MESSAGE
    criteria_result = messages.data[0].content[0].text.value
    #criteria_result = messages.data[0]

    return criteria_result
