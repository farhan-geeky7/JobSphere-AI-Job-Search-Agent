# JobSphere — AI Job Search & Matching Agent

JobSphere is a Python and FastAPI-based project designed to help job seekers discover relevant opportunities by comparing job listings with their skills and career preferences.

The project includes a web dashboard, job-source integrations, job-matching logic, and experimental browser-based application assistance.

## Dashboard Preview

### Homepage

![JobSphere Homepage](docs/screenshots/homepage.png)

### Resume Upload and Job Search

![Resume Upload and Job Search](docs/screenshots/resume-upload.png)

### How It Works

![How JobSphere Works](docs/screenshots/how-it-works.png)

## Key Features

- **Job Discovery:** Collect job listings from configured job sources.
- **Job Matching:** Evaluate available jobs against profile details and role preferences.
- **Web Dashboard:** Access the project through a browser-based interface.
- **Resume Workflow:** Resume upload and profile analysis are part of the intended workflow; verify the current implementation before relying on every step.
- **Application Assistance:** Experimental modules explore application-page analysis and form-filling support.

## How It Works

1. Start the FastAPI backend.
2. Open the JobSphere dashboard.
3. Enter job preferences and provide a resume where supported.
4. Retrieve jobs from configured sources.
5. Review the available matches and visit the original job postings.

## Technology Stack

- Python
- FastAPI
- HTML, CSS and JavaScript
- Job aggregation and matching modules
- Browser automation components

## Getting Started

### Prerequisites

- Python 3.10 or later
- Git

### Installation

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/JobSphere-AI-Job-Search-Agent.git
cd JobSphere-AI-Job-Search-Agent
```

Create and activate a virtual environment from the project root:

**Windows PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project dependencies after a root-level `requirements.txt` has been provided:

```bash
pip install -r requirements.txt
```

### Run the Backend

```powershell
cd backend
python -m uvicorn main:app --reload
```

Open the dashboard:

http://127.0.0.1:8000/dashboard

Interactive API documentation may be available at:

http://127.0.0.1:8000/docs

> Note: Fresh-install instructions depend on the final dependency list. The project currently uses a backend virtual environment; setup commands may need adjustment until dependencies are documented.

## Project Structure

```text
JobSphere/
├── backend/
│   ├── agent/
│   ├── frontend/
│   ├── job_sources/
│   ├── models/
│   └── main.py
├── docs/
│   └── screenshots/
├── .gitignore
└── README.md
```

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned improvements and development priorities.

## Current Status

JobSphere is a work in progress. Job-source availability, matching quality, resume handling, and browser automation require ongoing testing. Application submission should always be reviewed and authorized by the user.

## Contributing

Issues, suggestions, and improvements are welcome. Please describe bugs clearly and include reproduction steps where possible.

## Disclaimer

This project is intended to assist with job discovery and matching. Always verify job details on the original employer or job-platform website before sharing personal information or applying.

## Author

Created as a project to explore Python, FastAPI, job aggregation, resume matching, and browser automation.