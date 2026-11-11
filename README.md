# AI Interview Analyzer

An AI-powered interview platform that allows HR teams to create job openings, candidates to apply and attend AI-powered interviews, and HR teams to review interview reports and speech-delivery metrics.

## 1. Prerequisites

Install the following before setting up the project:

- Python 3.10+
- MySQL Server
- MySQL Workbench or DBeaver
- Visual Studio Code (recommended)
- Git

## 2. Clone the Repository

```bash
git clone <your-repository-url>
cd "ai interview analyzer"
```

## 3. Create a Virtual Environment

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate the environment.

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

## 4. Install Dependencies

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## 5. Configure MySQL Database

Open MySQL Workbench or DBeaver and execute:

```sql
CREATE DATABASE ai_interview_analyzer;
```

## 6. Configure Environment Variables

Create a `.env` file in the project root directory.

Add the following configuration:

```env
DATABASE_URL=mysql+pymysql://<username>:<password>@localhost:3306/ai_interview_analyzer

NVIDIA_API_KEY=<your_nvidia_api_key>
```

Replace the placeholders with your MySQL credentials and NVIDIA API key.

**Important:** Never commit your `.env` file or expose API keys in the repository.

## 7. Create Database Tables

After defining the SQLAlchemy models and configuring the database connection, run the table creation command.

```bash
python -c "from backend.database import Base, engine; from backend.models import *; Base.metadata.create_all(bind=engine)"
```

This creates the database tables defined by the imported SQLAlchemy models.

Verify that the tables have been created using MySQL Workbench or DBeaver.

## 8. Run the FastAPI Backend

From the project root directory, activate the virtual environment and execute:

```bash
uvicorn backend.main:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

## 9. Access API Documentation

FastAPI provides interactive API documentation.

Open the following URL in your browser:

```text
http://127.0.0.1:8000/docs
```

Use Swagger UI to explore and test the available API endpoints.

## 10. Useful Development Commands

**Check installed dependencies:**
```bash
pip list
```

**Install a new dependency:**
```bash
pip install package-name
```

**Update requirements.txt:**
```bash
pip freeze > requirements.txt
```

**Deactivate virtual environment:**
```bash
deactivate
```

**Run FastAPI with automatic reload:**
```bash
uvicorn backend.main:app --reload
```

## Project Development Workflow

1. Configure the MySQL database.
2. Create SQLAlchemy models and database relationships.
3. Implement user registration and login.
4. Implement HR job creation and candidate applications.
5. Integrate the AI interview and audio analysis pipeline.
6. Store interview conversations and generate final reports.
7. Build the React frontend.
8. Implement interview report generation and PDF downloads.

## Notes

- Always run backend commands from the project root directory.
- Ensure the virtual environment is activated before installing dependencies or running the backend.
- Ensure MySQL Server is running before starting the application.
- Keep API keys and database credentials in `.env`.
- Do not commit `.venv/`, `.env`, or generated model/cache files to Git.
