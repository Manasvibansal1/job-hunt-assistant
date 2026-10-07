from crewai import Agent, Task
from langchain_openai import ChatOpenAI
import os

groq_llm = ChatOpenAI(
    model="openai/gpt-oss-20b",
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0.2
)

def get_resume_cl_agent():
    return Agent(
        role="Resume & Cover Letter Strategist",
        goal="Tailor resumes and draft targeted cover letters for federal job descriptions",
        backstory="You are an expert technical resume writer and career coach specializing in federal government applications.",
        llm=groq_llm,
        verbose=True
    )
    
def create_resume_cl_task(agent, job_description, resume_text):
    return Task(
        description=f"""
        Tailor the candidate's resume for the given job description and write a cover letter.
        
        CRITICAL FORMATTING INSTRUCTIONS:
        Your response must include these exact markers:
        <<RESUME_SUMMARY>>
        [Provide a summary of the tailored resume changes here]
        <<COVER_LETTER>>
        [Provide the full cover letter text here]
        
        Candidate Resume:
        {resume_text}
        
        Job Description:
        {job_description}
        """,
        expected_output="Plain text containing <<RESUME_SUMMARY>> and <<COVER_LETTER>> markers with the corresponding content.",
        agent=agent,
        output_file='/usercode/job_hunt_assistant/data/resume_agent_output.txt'
    )