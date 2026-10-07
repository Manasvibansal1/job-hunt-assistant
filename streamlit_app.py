import streamlit as st
import os
from orchestrator import (
    run_pipeline, 
    generate_star_stories, 
    evaluate_fit_triage, 
    scan_job_risks, 
    convert_to_federal_format, 
    generate_follow_up_draft, 
    check_pending_follow_ups
)
from usajobs_api import fetch_usajobs
from india_api import fetch_india_jobs
from jooble_api import fetch_jooble_jobs

st.title("Federal & Global Job Application Assistant")
st.markdown("""
Multi-region intelligence system equipped with fit triage, risk auditing, federal resume conversion, STAR storytelling, and lifecycle follow-up tracking.
""")

# Sidebar inputs
st.sidebar.header("Application Parameters")

country_choice = st.sidebar.selectbox(
    "Select Region / Source", 
    ["United States (USAJobs)", "India (Adzuna)", "Global / Multi-Country (Jooble)"]
)
keyword = st.sidebar.text_input("Job Keyword", "Data Analyst")
location = st.sidebar.text_input("Location", "Washington, DC" if "United States" in country_choice else "New Delhi")

user_resume = st.sidebar.text_area("Candidate Resume Text", "Enter your resume text here...")
user_bio = st.sidebar.text_area("Candidate Bio", "Enter your professional bio here...")
story_bank = st.sidebar.text_area("Candidate Story Bank (STAR)", "Enter past projects/challenges here...")

if st.sidebar.button("Search Jobs"):
    with st.spinner("Searching job boards..."):
        if "India" in country_choice:
            st.session_state.jobs = fetch_india_jobs(keyword, location)
        elif "Jooble" in country_choice:
            st.session_state.jobs = fetch_jooble_jobs(keyword, location)
        else:
            st.session_state.jobs = fetch_usajobs(keyword, location)

if "jobs" not in st.session_state:
    st.session_state.jobs = []

selected_jobs = []

if st.session_state.jobs:
    st.subheader("Select Job Postings to Process")
    for idx, job in enumerate(st.session_state.jobs):
        # Robust parsing across different API schemas
        descriptor = job.get('MatchedObjectDescriptor', job)
        
        job_title = (
            job.get('PositionTitle') or 
            descriptor.get('PositionTitle') or 
            job.get('title') or 
            'Unknown Position'
        )
        
        agency_name = (
            job.get('OrganizationName') or 
            descriptor.get('OrganizationName') or 
            job.get('company') or 
            'Unknown Agency'
        )
        
        is_selected = st.checkbox(f"**{job_title}** at {agency_name}", key=f"job_{idx}")
        if is_selected:
            selected_jobs.append(job)

    st.markdown("---")
    
    # Action Buttons Grid
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        triage_clicked = st.button("1. Run Fit Triage")
    with col2:
        risk_clicked = st.button("2. Scan Risks & Ghost Status")
    with col3:
        apply_clicked = st.button("3. Full Pipeline & Apply")
    with col4:
        star_clicked = st.button("4. STAR Interview Stories")

    federal_clicked = False
    if "United States" in country_choice:
        federal_clicked = st.button("Convert Resume to Strict Federal Format")

    # --- 1. FIT TRIAGE ---
    if triage_clicked:
        if not selected_jobs:
            st.warning("Please select at least one job posting.")
        else:
            for job in selected_jobs:
                descriptor = job.get('MatchedObjectDescriptor', job)
                title = job.get('PositionTitle') or descriptor.get('PositionTitle') or job.get('title') or 'Unknown Position'
                summary = descriptor.get('JobSummary', job.get('JobSummary', ''))
                
                with st.spinner(f"Evaluating fit triage for {title}..."):
                    triage_result = evaluate_fit_triage(summary, user_resume)
                    st.subheader(f"📊 Fit Triage: {title}")
                    st.markdown(triage_result)
                    st.markdown("---")

    # --- 2. RISK & GHOST JOB SCANNER ---
    if risk_clicked:
        if not selected_jobs:
            st.warning("Please select at least one job posting.")
        else:
            for job in selected_jobs:
                descriptor = job.get('MatchedObjectDescriptor', job)
                title = job.get('PositionTitle') or descriptor.get('PositionTitle') or job.get('title') or 'Unknown Position'
                summary = descriptor.get('JobSummary', job.get('JobSummary', ''))
                
                with st.spinner(f"Scanning risks and ghost status for {title}..."):
                    risk_report = scan_job_risks(job, summary)
                    st.subheader(f"🛡️ Risk & Ghost Job Oracle: {title}")
                    st.markdown(risk_report)
                    st.markdown("---")

    # --- 3. FULL PIPELINE & APPLICATION ---
    if apply_clicked:
        if not selected_jobs:
            st.warning("Please select at least one job posting.")
        else:
            for idx, job in enumerate(selected_jobs):
                descriptor = job.get('MatchedObjectDescriptor', job)
                job_title = job.get('PositionTitle') or descriptor.get('PositionTitle') or job.get('title') or 'Unknown Position'
                agency_name = job.get('OrganizationName') or descriptor.get('OrganizationName') or job.get('company') or 'Unknown Agency'
                
                with st.spinner(f"Processing application for {job_title}..."):
                    try:
                        outreach_message = run_pipeline(job, user_resume, user_bio)
                        st.success(f"Successfully processed: {job_title} at {agency_name}")
                        st.markdown(outreach_message)
                        
                        cover_letter_dir = os.path.join(os.path.dirname(__file__), 'data', 'cover_letters')
                        if os.path.exists(cover_letter_dir):
                            matching_files = sorted([os.path.join(cover_letter_dir, f) for f in os.listdir(cover_letter_dir)], key=os.path.getmtime, reverse=True)
                            if matching_files:
                                with open(matching_files[0], "rb") as file_btn:
                                    st.download_button("Download Cover Letter (.txt)", file_btn, file_name=os.path.basename(matching_files[0]), mime="text/plain", key=f"cl_{idx}")
                        
                        log_path = os.path.join(os.path.dirname(__file__), 'data', 'applications_log.csv')
                        if os.path.exists(log_path):
                            with open(log_path, "rb") as log_btn:
                                st.download_button("Download Tracking Log (CSV)", log_btn, file_name="applications_log.csv", mime="text/csv", key=f"log_{idx}")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # --- 4. STAR STORIES ---
    if star_clicked:
        if not selected_jobs or not story_bank.strip():
            st.warning("Please select a job and populate your STAR Story Bank in the sidebar.")
        else:
            for job in selected_jobs:
                descriptor = job.get('MatchedObjectDescriptor', job)
                title = job.get('PositionTitle') or descriptor.get('PositionTitle') or job.get('title') or 'Unknown Position'
                summary = descriptor.get('JobSummary', job.get('JobSummary', ''))
                with st.spinner(f"Generating STAR stories for {title}..."):
                    st.markdown(generate_star_stories(story_bank, summary))

    # --- 5. FEDERAL RESUME CONVERTER ---
    if federal_clicked:
        if not selected_jobs:
            st.warning("Please select a federal job posting.")
        else:
            for job in selected_jobs:
                descriptor = job.get('MatchedObjectDescriptor', job)
                title = job.get('PositionTitle') or descriptor.get('PositionTitle') or job.get('title') or 'Unknown Position'
                summary = descriptor.get('JobSummary', job.get('JobSummary', ''))
                with st.spinner(f"Formatting strict federal resume for {title}..."):
                    fed_resume = convert_to_federal_format(user_resume, summary)
                    st.subheader(f"🇺🇸 Federal Resume Format: {title}")
                    st.markdown(fed_resume)

else:
    st.info("Use the sidebar to search for and load job postings.")

# --- 6. SMART FOLLOW-UP SCHEDULER WIDGET ---
st.markdown("---")
st.subheader("📬 Smart Follow-Up Scheduler")
pending_follows = check_pending_follow_ups()

if pending_follows:
    st.warning(f"You have {len(pending_follows)} application(s) older than 5 days without a status update!")
    for item in pending_follows:
        st.write(f"- **{item['Job Title']}** at **{item['Agency']}** ({item['Days Ago']} days ago)")
        if st.button(f"Draft Follow-Up Email for {item['Job Title']}", key=f"follow_{item['Job Title']}"):
            draft = generate_follow_up_draft(item['Job Title'], item['Agency'])
            st.code(draft, language="markdown")
else:
    st.success("All recent applications are within their initial window or logged successfully!")