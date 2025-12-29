# GCP Authentication Guide for Vertex AI Agent

To enable the AI Agent to communicate with Google Gemini models, you must provide authentication credentials.

## Step 1: Install Google Cloud CLI
If you haven't installed the `gcloud` CLI yet, follow the official instructions:
https://cloud.google.com/sdk/docs/install

## Step 2: Login
Run the following command in your terminal. This will open a browser window for you to log in with your Google account.

**Option A (Standard):**
```bash
gcloud auth application-default login
```

**Option B (If "command not found"):**
Use the absolute path to the installed SDK:
**Option C (Most Reliable):**
If the browser doesn't open or you get consent errors, use this:
```bash
./google-cloud-sdk/bin/gcloud auth application-default login --no-browser
```
*   Copy the long URL from the terminal into your browser.
*   Log in and **ALLOW** all permissions.
*   Copy the code back to the terminal.

## Step 3: Set Project ID
Ensure your environment is using the correct project ID.
```bash
gcloud config set project [YOUR_PROJECT_ID]
```

## Step 4: Enable APIs
Make sure the **Vertex AI API** is enabled for your project in the Google Cloud Console.
https://console.cloud.google.com/vertex-ai

## Verification
After logging in, restart the Streamlit app:
```bash
source venv/bin/activate
streamlit run app.py
```
