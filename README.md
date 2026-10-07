# Enterprise AI Career Command Center

An enterprise-grade, multi-region intelligence system designed to automate, optimize, and de-risk the end-to-end job application lifecycle. Built with Python, Streamlit, LangChain, and Groq LLMs.

---

## Architecture & Core Capabilities

* **Multi-Region Job Sourcing:** Unified ingestion pipelines supporting USAJobs (Federal), Adzuna (India), and Jooble (Global/Multi-Country) REST APIs with robust schema mapping.
* **Pre-Execution Fit Triage:** Algorithmic scoring engine (0-100) evaluating candidate-to-job description alignment before expending LLM compute.
* **Risk & Ghost Job Oracle:** Metadata and text scanners that audit job postings for scam indicators, suspicious contact points, stale listings, and repost velocities.
* **Federal Resume Converter:** Automated formatting engine that expands corporate experience into rigorous government-compliant standards (incorporating exact dates, hours per week, and supervisor fields).
* **STAR Story Mapping:** Behavioral interview prep module that transforms raw professional project notes into structured Situation, Task, Action, Result competencies tailored to specific postings.
* **Lifecycle & Follow-Up Automation:** Local CSV persistence tracking with a proactive scheduler that flags stalled applications and auto-drafts touchpoint emails after 5+ days of silence.

---

## Tech Stack

* **Frontend / UI:** Streamlit
* **Orchestration & LLM:** LangChain, Groq API (`openai/gpt-oss-20b`)
* **Data & Persistence:** Pandas, Local CSV logs (`data/applications_log.csv`)
* **APIs:** USAJobs, Adzuna, Jooble REST APIs

---

## Project Structure


job_hunt_assistant/
│
├── streamlit_app.py        # Main Streamlit dashboard and UI routing
├── orchestrator.py         # Core agentic logic, LLM prompts, and analysis functions
├── usajobs_api.py          # USAJobs API integration fetcher
├── india_api.py            # Adzuna (India) API integration fetcher
├── jooble_api.py           # Jooble Global API integration fetcher
├── utils/                  # Tracking and file persistence utilities
│   └── tracking.py
├── data/                   # Output directory for logs, reports, and cover letters
│   └── applications_log.csv
├── requirements.txt        # Python package dependencies
└── README.md