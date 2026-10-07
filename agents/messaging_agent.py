from crewai import Agent, Task
from langchain_openai import ChatOpenAI
import os

groq_llm = ChatOpenAI(
    model="openai/gpt-oss-20b",
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0.2
)

def get_messaging_agent():
    return Agent(
        role="Networking & Outreach Specialist",
        goal="Draft tailored professional networking and outreach messages for government roles",
        backstory="You excel at writing concise, engaging professional messages that connect a candidate's background to specific agency needs.",
        llm=groq_llm,
        verbose=True
    )

def create_messaging_task(agent, job_description, agency_name, user_bio):
    return Task(
        description=f"""
        Draft a professional networking outreach message for a role at {agency_name}.
        Use the candidate bio and job description below.
        
        Candidate Bio:
        {user_bio}
        
        Job Description:
        {job_description}
        """,
        expected_output="Provide a text outreach message ready to be sent.",
        agent=agent,
        output_file='/usercode/job_hunt_assistant/data/messaging_agent_output.txt',
        async_execution=False
    )