# HR Data Intelligence Agent

This project is an end-to-end data engineering and analytics solution I built to make HR data accessible through natural language.

The goal was to solve a common problem: accessing insights from employee data usually requires writing complex SQL queries or asking a data analyst. I wanted to build a system where anyone could just ask, *"Who are the top performers in Sales?"* and get an immediate, accurate answer.
# HR  Agent 

## Project Overview
This project acts as an autonomous SQL Agent designed to answer queries about employee data with 100% precision. It features a "Double-Check" architecture where a primary Agent generates answers from a secure SQLite database, and a secondary "QA Critic" validates those answers before they are displayed.

**Business Value:**
- **Zero Hallucination:** The QA layer filters out incorrect or invented data.
- **Strict Logic:** Correctly handles ties, date sorting (tenure), and null values.
- **Audit Logging:** All queries and verification statuses are logged to `query_logs` for future model training.

---

## System Architecture
1.  **ETL Pipeline (src/etl.py):**
    -   Ingests raw CSV data.
    -   Validates schema (checks for required columns).
    -   Standardizes dates to ISO 8601 (YYYY-MM-DD).
    -   Deduplicates records based on normalized email.
2.  **Database (src/db.py):**
    -   Loads cleaned data into an in-memory SQLite instance.
    -   Maintains a `query_logs` table for persistent interaction history.
3.  **Core Agent (src/agent.py):**
    -   Powered by Google Vertex AI (Gemini Flash).
    -   Uses strict Prompt Engineering to enforce Table output and date sanity.
4.  **Application (app.py):**
    -   Streamlit-based UI.
    -   Pure Chat interface (no legacy dashboard).
    -   Real-time "Verified Correct" feedback badges.

---

## Setup Instructions

### Prerequisites
- Python 3.9+
- Google Cloud Project with Vertex AI API enabled.
- `gcloud` CLI installed and authenticated.

### 1. Environment Configuration
Create a `.env` file in the root directory:
```bash
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_LOCATION=us-central1
VERTEX_MODEL_NAME=gemini-2.5-flash
```

### 2. Installation
Install dependencies using pip:
```bash
pip install -r requirements.txt
```

### 3. Authentication
Authenticate your local session with Google Cloud:
```bash
gcloud auth application-default login
```

### 4. Data Processing (ETL)
Run the pipeline to generate the clean dataset:
```bash
python -m src.etl
```
*Expected Output:*
> INFO - Pipeline finished. Cleaned data saved to data/processed/cleaned_employees.csv

### 5. Launch Application
Run the Streamlit server:
```bash
streamlit run app.py
```
Access the UI at `http://localhost:8501`.

---

## Usage Guide
Ask specific questions about the data. The Agent supports:
- **Aggregation:** "What is the average salary by department?"
- **Filtering:** "List all employees in Sales joined before 2021."
- **Reasoning:** "Who is the most tenured employee in Update?"

**Verification Badge Guide:**
- **Green Badge:** The QA Critic confirmed the answer matches the database facts.
- **Yellow/Warning Badge:** The QA Critic detected a potential hallucination or logic error.

## Troubleshooting
- **Date Errors:** If dates appear unsorted, ensure you ran `python -m src.etl` to enforce YYYY-MM-DD format.
- **Auth Errors:** Run `gcloud auth application-default login` again if the Agent fails to initialize.

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
cd HR_Agent

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
cd HR_Agent

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
