# Financial Analysis Dashboard

This project is a web application for financial analysis, offering stock data retrieval, sentiment analysis, SEC report analysis, and an interactive chatbot for financial guidance. The application uses Flask as the backend, HTML/CSS/JavaScript for the frontend, and integrates with AWS Bedrock for Claude-based financial analysis.

## Table of Contents
1. [Features](#features)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Environment Setup](#environment-setup)
5. [Running the Application](#running-the-application)
6. [Usage](#usage)
7. [Troubleshooting](#troubleshooting)

---

## Features

- **Stock Data Analysis**: Real-time stock data visualizations using Chart.js.
- **Sentiment and Metrics Display**: View metrics such as revenue, free cash flow, and risk levels.
- **SEC Report Retrieval**: Retrieve and analyze SEC filings (10-K, 10-Q, 8-K, DEF 14A).
- **AI Chatbot**: Chat with a financial advisor powered by Claude via AWS Bedrock.

---

## Requirements

- **Python** 3.7 or higher
- **Node.js** (optional, for frontend dependencies if needed)
- **AWS Account** to access Bedrock API
- **Pip** for package management

---

## Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/taylcr/Financial-Analysis/FINAL_BRANCH
    cd financial-analysis-dashboard
    ```

2. **Create `requirements.txt`**:
   Add the following to `requirements.txt`:
   ```plaintext
   Flask==2.2.2
   Flask-Cors==3.0.10
   yfinance==0.2.26
   openai==0.27.0
   boto3==1.28.6
   requests==2.31.0
   python-dotenv==1.0.0
   beautifulsoup4==4.12.2

3.Install Backend Dependencies:
  pip install -r requirements.txt

Frontend Dependencies:

Chart.js: Integrated via CDN.
Font Awesome: Integrated via CDN.
Additional JavaScript Libraries:

Moment.js and jQuery are used for date handling and DOM manipulation, included via CDN.

Environment Setup
Create an .env File in the root directory to configure AWS credentials for Bedrock. Populate it with:

AWS_ACCESS_KEY_ID=<YOUR_AWS_ACCESS_KEY_ID>
AWS_SECRET_ACCESS_KEY=<YOUR_AWS_SECRET_ACCESS_KEY>
AWS_SESSION_TOKEN=<YOUR_AWS_SESSION_TOKEN>
AWS_DEFAULT_REGION=<YOUR_AWS_REGION>

Add Required Keys:

Ensure the environment variables include AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, and AWS_DEFAULT_REGION.


Running the Application
Start the Flask App:

python app.py

  This command will start the Flask server on http://127.0.0.1:5000.

  Access the Dashboard:

  Open your browser and navigate to http://127.0.0.1:5000.


Usage
  Search for a Stock: Enter a ticker symbol in the search bar to fetch stock data.
  Analyze SEC Reports: Select the year and form type, then click Retrieve Report to analyze.
  Chat with Financial Advisor: Click the chat icon to interact with the AI advisor for financial guidance.
  Troubleshooting
  Common Errors and Fixes
  AWS Bedrock Authentication Issues:
  
  Ensure your .env file has valid AWS credentials.
  Flask Server Errors:

      pip install -r requirements.txt



