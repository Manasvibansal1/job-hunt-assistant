import os
import pandas as pd
from datetime import datetime
from langchain_openai import ChatOpenAI
from utils.tracking import log_application, save_cover_letter_file

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def extract_between_markers(text, start_marker, end_marker=None):
    """Helper function to extract text between markers or from a start marker to the end."""
    try:
        start = text.index(start_marker) + len(start_marker)
        if end_marker:
            end = text.index(end_marker, start)
            return text[start:end].strip()
        else:
            return text[start:].strip()
    except ValueError:
        return text.strip()

def run_pipeline(job_data, resume_text, user_bio):
    """Executes the pipeline directly via LLM to bypass CrewAI parsing crashes."""
    descriptor = job_data.get('MatchedObjectDescriptor', job_data)
    
    job_summary = descriptor.get('UserArea', {}).get('Details', {}).get('JobSummary', job_data.get('JobSummary', 'No summary available.'))
    agency_name = descriptor.get('OrganizationName', job_data.get('OrganizationName', 'Unknown Agency'))
    job_title = descriptor.get('PositionTitle', job_data.get('PositionTitle', 'Unknown Position'))

    llm = ChatOpenAI(
        model="openai/gpt-oss-20b",
        openai_api_base="https://api.groq.com/openai/v1",
        openai_api_key=os.environ.get("GROQ_API_KEY"),
        temperature=0.2
    )

    os.makedirs(DATA_DIR, exist_ok=True)

    # 1. JD Analysis
    analysis_prompt = f"Analyze the following job posting and extract a summary, key skills, and qualifications:\n\n{job_summary}"
    report_result = llm.invoke(analysis_prompt).content
    with open(os.path.join(DATA_DIR, 'report.md'), 'w', encoding='utf-8') as f:
        f.write(report_result)

    # 2. Resume & Cover Letter Generation
    resume_prompt = f"""
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
    {job_summary}
    """
    resume_output = llm.invoke(resume_prompt).content
    with open(os.path.join(DATA_DIR, 'resume_agent_output.txt'), 'w', encoding='utf-8') as f:
        f.write(resume_output)

    resume_summary = extract_between_markers(resume_output, "<<RESUME_SUMMARY>>", "<<COVER_LETTER>>")
    cover_letter = extract_between_markers(resume_output, "<<COVER_LETTER>>")

    # 3. Messaging Outreach
    msg_prompt = f"Draft a professional networking outreach message for a role as {job_title} at {agency_name} using this candidate bio:\n{user_bio}\nAnd job description:\n{job_summary}"
    msg_result = llm.invoke(msg_prompt).content
    with open(os.path.join(DATA_DIR, 'messaging_agent_output.txt'), 'w', encoding='utf-8') as f:
        f.write(msg_result)

    log_application(job_title, agency_name, resume_summary)
    save_cover_letter_file(job_title, cover_letter)

    return msg_result


def generate_star_stories(story_bank, job_summary):
    """Transforms a raw story bank into structured STAR format tailored to the target job description."""
    llm = ChatOpenAI(
        model="openai/gpt-oss-20b",
        openai_api_base="https://api.groq.com/openai/v1",
        openai_api_key=os.environ.get("GROQ_API_KEY"),
        temperature=0.3
    )
    
    star_prompt = f"""
    You are an expert interview coach. Review the target job description:
    {job_summary}
    
    And review the candidate's raw professional experience stories:
    {story_bank}
    
    Task: Transform these raw notes into 2-3 structured STAR (Situation, Task, Action, Result) responses. 
    Align the language, metrics, and core competencies to match what the job description demands.
    
    Format each story clearly with bold headings:
    ### Story [Number]: [Descriptive Title]
    - **Situation:** ...
    - **Task:** ...
    - **Action:** ...
    - **Result:** ...
    """
    return llm.invoke(star_prompt).content


def evaluate_fit_triage(job_summary, resume_text):
    """Scores the job fit (0-100) and provides a quick rationale before running the full pipeline."""
    llm = ChatOpenAI(
        model="openai/gpt-oss-20b",
        openai_api_base="https://api.groq.com/openai/v1",
        openai_api_key=os.environ.get("GROQ_API_KEY"),
        temperature=0.1
    )
    prompt = f"""
    Analyze the alignment between the candidate resume and the job description.
    Provide a Fit Triage Score from 0 to 100, followed by a 2-sentence rationale.
    
    Format:
    **Score:** [XX]/100
    **Rationale:** [Short explanation of match quality and gaps]
    
    Resume:
    {resume_text}
    
    Job Description:
    {job_summary}
    """
    return llm.invoke(prompt).content


def scan_job_risks(job_data, job_summary):
    """Scans for scam flags (fees, personal emails) and ghost job / repost patterns."""
    descriptor = job_data.get('MatchedObjectDescriptor', job_data)
    posting_date = descriptor.get('PublicationStartDate', descriptor.get('created', job_data.get('PublicationStartDate', 'Unknown')))
    
    llm = ChatOpenAI(
        model="openai/gpt-oss-20b",
        openai_api_base="https://api.groq.com/openai/v1",
        openai_api_key=os.environ.get("GROQ_API_KEY"),
        temperature=0.1
    )
    prompt = f"""
    Analyze this job posting data and text for potential scams and ghost-job indicators (e.g., vague requirements, repost velocity, suspicious contact info).
    Posting Date provided: {posting_date}
    
    Job Description:
    {job_summary}
    
    Provide your analysis in two sections:
    1. **Scam & Red-Flag Audit:** (Safe / Suspicious with reasons)
    2. **Ghost Job / Realness Index:** (High Probability / Low Probability of active hiring)
    """
    return llm.invoke(prompt).content


def convert_to_federal_format(resume_text, job_summary):
    """Expands standard resume bullets into rigorous federal format (exact dates, hours/week, supervisor placeholders)."""
    llm = ChatOpenAI(
        model="openai/gpt-oss-20b",
        openai_api_base="https://api.groq.com/openai/v1",
        openai_api_key=os.environ.get("GROQ_API_KEY"),
        temperature=0.2
    )
    prompt = f"""
    You are an expert federal resume writer (USAJobs specialist). Federal resumes require granular detail: exact start/end dates (MM/YYYY), average hours worked per week (e.g., 40 hrs/week), supervisor names/contacts placeholders, and detailed duties mapping directly to the job qualifications.
    
    Target Job:
    {job_summary}
    
    Candidate Resume:
    {resume_text}
    
    Rewrite/format the experience section to meet strict federal standards.
    """
    return llm.invoke(prompt).content


def generate_follow_up_draft(job_title, agency_name):
    """Generates a professional follow-up email for applications sitting with no reply."""
    llm = ChatOpenAI(
        model="openai/gpt-oss-20b",
        openai_api_base="https://api.groq.com/openai/v1",
        openai_api_key=os.environ.get("GROQ_API_KEY"),
        temperature=0.3
    )
    prompt = f"""
    Draft a polite, professional, and concise follow-up email for an application submitted for the role of {job_title} at {agency_name}. 
    It has been over a week with no status update. Reiterate enthusiasm and offer additional information if needed.
    """
    return llm.invoke(prompt).content


def check_pending_follow_ups():
    """Scans the application log CSV to find applications aged 5-10+ days without updates."""
    log_path = os.path.join(DATA_DIR, 'applications_log.csv')
    if not os.path.exists(log_path):
        return []
    
    try:
        df = pd.read_csv(log_path)
        if df.empty or 'Timestamp' not in df.columns:
            return []
        
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        now = datetime.now()
        
        pending = []
        for _, row in df.iterrows():
            app_date = row['Timestamp']
            if pd.notnull(app_date):
                days_elapsed = (now - app_date).days
                if days_elapsed >= 5:
                    pending.append({
                        "Job Title": row.get('Job Title', 'Unknown Position'),
                        "Agency": row.get('Agency', 'Unknown Agency'),
                        "Days Ago": days_elapsed
                    })
        return pending
    except Exception:
        return []