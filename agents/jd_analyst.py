from crewai import Agent, Task
from langchain_openai import ChatOpenAI
import os

groq_llm = ChatOpenAI(
    model="openai/gpt-oss-20b",
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0.2
)

def get_jd_analyst_agent():
    return Agent(
        role="JD Analyst",
        goal="Understand and summarize government job postings",
        backstory="You're an expert in job market analysis with a focus on US federal job listings.",
        llm=groq_llm,
        verbose=True
    )

def create_jd_analysis_task(agent, job_description):
    return Task(
        description=f"""
        Analyze the following USAJobs job posting and extract:
        - A summary of the role
        - Key skills required
        - Any specific qualifications or eligibility
        
        Job Description:
        {job_description}
        """,
        expected_output="Provide a text summary of the role requirements.",
        agent=agent,
        output_file='/usercode/job_hunt_assistant/data/report.md',
        async_execution=False
    )