# Task Tracker API

A REST API for tracking tasks, built with Python and FastAPI. This repository currently provides the project skeleton and a health check endpoint.

## Setup

1. Create a virtual environment and install dependencies

**Linux/macOS:**
\`\`\`bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\`\`\`

**Windows (PowerShell):**
\`\`\`powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
\`\`\`

## Running the server

\`\`\`bash
uvicorn app.main:app --reload --port 8000
\`\`\`
The API will be available at `http://localhost:8000`.

## Running front end
cd frontend    
python -m http.server 5500 

