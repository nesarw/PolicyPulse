# PolicyPulse

[![Streamlit Cloud](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/) <!-- TODO: Replace with your app's Streamlit Cloud URL -->

## Overview

PolicyPulse is an interactive Streamlit application designed to help users analyze, discuss, and visualize policy documents and related data. With a conversational interface and context-aware features, PolicyPulse aims to make policy analysis more accessible and engaging for everyone.

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nesarw/PolicyPulse.git
   cd PolicyPulse
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   ```

3. **Activate the virtual environment:**
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running Locally

You can use the provided script to set up and launch the app:

```bash
./run.sh
```

Or, run manually:

```bash
streamlit run app.py
```

## Streamlit Cloud

[![Open in Streamlit Cloud](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)  
*Replace this link with your deployed app's Streamlit Cloud URL.*

## BFSI Domain Restriction

PolicyPulse is strictly limited to answering questions related to the Banking, Financial Services, and Insurance (BFSI) sector. Any questions outside this domain (e.g., programming, sports, general trivia) will be politely refused by the assistant.

This is enforced by a BFSI domain filter utility (`utils/bfsi_filter.py`) that checks user queries for BFSI relevance before generating a response. You can customize the list of keywords in that file to broaden or narrow the domain as needed.

## Features
- Conversational interface for BFSI policy and insurance queries
- Strict refusal to answer out-of-domain questions
- Context-aware answers with related suggestions
- Easy extensibility for BFSI topics