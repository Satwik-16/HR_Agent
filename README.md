# HR Data Intelligence Agent

This project is an end-to-end data engineering and analytics solution I built to make HR data accessible through natural language.

The goal was to solve a common problem: accessing insights from employee data usually requires writing complex SQL queries or asking a data analyst. I wanted to build a system where anyone could just ask, *"Who are the top performers in Sales?"* and get an immediate, accurate answer.

## How It Works

I designed this application with three main components:

1.  **ETL Pipeline (`src/etl.py`):** I wrote a robust pipeline to ingest raw CSV data. It doesn't just copy data; it validates the schema, deduplicates records based on normalized emails, and cleans up messy formats like phone numbers and salaries.
2.  **SQL Agent (`src/agent.py`):** Instead of letting an LLM guess answers from text, I used a **SQL Agent** architecture. The Agent (powered by Google Gemini) generates SQL queries to run against a local database. This maximizes accuracy—math operations like "average salary" are done by the database, not the LLM.
3.  **Analytics Interface (`app.py`):** I built a clean Streamlit app that serves as the front end. It combines the chat interface with a dynamic dashboard for quick high-level metrics.

---

## Setup Guide

I've made the setup process as standard as possible so you can run it on macOS, Linux, or Windows.

### 1. Prerequisites
You'll need **Python 3.10+** and the **Google Cloud SDK** installed.

### 2. Environment Setup

**macOS / Linux:**
```bash
# Clone and enter the repo
git clone <repo-url>
cd Alation

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
# Clone and enter the repo
git clone <repo-url>
cd Alation

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

You need to connect the app to Google Cloud Vertex AI.

1.  Copy the example config:
    *   **Mac:** `cp .env.example .env`
    *   **Windows:** `copy .env.example .env`
2.  Open `.env` and add your **Google Project ID**.
3.  Authenticate your session:
    ```bash
    gcloud auth application-default login
    ```

---

## Running the Project

### Step 1: Process the Data
Run the ETL pipeline first. This ensures we aren't querying raw, dirty data.
```bash
python -m src.etl
```
*You should see logs confirming that the database was created in `data/processed/hr.db`.*

### Step 2: Start the App
Launch the interface:
```bash
streamlit run app.py
```
The app will open in your browser at `http://localhost:8501`.

---

## Architecture Decisions

*   **Why SQLite?** I chose SQLite for this implementation because it's serverless and handles the dataset size easily without needing a separate Docker container for Postgres. It makes replication for other engineers trivial.
*   **Why Streamlit?** It allowed me to iterate quickly on the UI. I stripped away the default sidebar and styled it with custom CSS to give it a cleaner, more "chat-native" feel than the default data app look.
*   **Security:** The AI Agent is restricted to **read-only** SQL permissions. It cannot modify employee records, ensuring data integrity is preserved.

If you run into any issues with the setup, let me know.
