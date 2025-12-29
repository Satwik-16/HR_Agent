# Credentials & Security Guide

This project uses **Google Application Default Credentials (ADC)** to securely authenticate with Vertex AI. This is the industry-standard method for local development, avoiding the need to download insecure JSON key files.

## 1. Quick Setup (The Golden Path)
Run this single command to authorize your local environment:

```bash
gcloud auth application-default login
```
*   This will open your browser.
*   Log in with the Google Account linked to your GCP Project.
*   Click "Allow".

## 2. Verify Configuration
Ensure your terminal points to the correct project:
```bash
gcloud config set project [YOUR_PROJECT_ID]
```

## 3. Scalability & Performance Note
The current architecture is optimized for:
*   **Small to Mid-Size Data**: Handles 100 - 50,000 employee records with sub-second latency.
*   **Memory**: Uses SQLite (file-based), which is robust for up to ~1GB of data.
*   **Safety**: The Agent queries the DB, not the LLM context window. This means it **can** scale to larger datasets (10k+ rows) without hitting token limits, as long as the *result* (e.g. "Top 5 employees") is concise.

## 4. Troubleshooting
**"403 Permission Denied":**
*   **Cause**: You logged in, but the API isn't enabled.
*   **Fix**: Go to [Vertex AI Console](https://console.cloud.google.com/vertex-ai) and click **"ENABLE API"**.

**"404 Model Not Found":**
*   **Cause**: The project ID in `.env` doesn't match your `gcloud` login.
*   **Fix**: Check `echo $GOOGLE_PROJECT_ID` vs `.env`.

