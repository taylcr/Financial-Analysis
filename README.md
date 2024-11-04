Financial Analysis Dashboard
This project is a web application for conducting financial analysis, including stock data retrieval, sentiment analysis, SEC report analysis, and an interactive chatbot for financial guidance. The application uses Flask as the backend, HTML/CSS/JavaScript for the frontend, and integrates with AWS Bedrock for Claude-based financial analysis.

Table of Contents
Features
Requirements
Installation
Environment Setup
Running the Application
Usage
Troubleshooting
Features
Stock Data Analysis: Real-time stock data with visualizations using Chart.js.
Sentiment and Metrics Display: View metrics such as revenue, free cash flow, and risk levels.
SEC Report Retrieval: Retrieve and analyze SEC filings (10-K, 10-Q, 8-K, DEF 14A).
AI Chatbot: Chat with a financial advisor powered by Claude via AWS Bedrock.
Requirements
Python 3.7 or higher
Node.js for frontend dependencies
AWS Account to access Bedrock API (configure .env for AWS credentials)
Pip for package management
Installation
Clone the Repository:

bash
Copy code
git clone <repo_url>
cd financial-analysis-dashboard
Install Backend Dependencies:

bash
Copy code
pip install -r requirements.txt
Frontend Dependencies:

Chart.js: Integrated via CDN.
Font Awesome: Integrated via CDN.
Additional JavaScript Libraries:

Moment.js and jQuery are used for date handling and DOM manipulation, included via CDN links.
Environment Setup
Create an .env File in the root directory to configure AWS credentials for Bedrock. Populate with:

plaintext
Copy code
AWS_ACCESS_KEY_ID=<YOUR_AWS_ACCESS_KEY_ID>
AWS_SECRET_ACCESS_KEY=<YOUR_AWS_SECRET_ACCESS_KEY>
AWS_SESSION_TOKEN=<YOUR_AWS_SESSION_TOKEN>
AWS_DEFAULT_REGION=<YOUR_AWS_REGION>
Add Required Keys:

Ensure the environment variables include AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN, and AWS_DEFAULT_REGION.
Running the Application
Start the Flask App:

bash
Copy code
python app.py
This command will start the Flask server on http://127.0.0.1:5000.

Access the Dashboard:

Open your browser and navigate to http://127.0.0.1:5000.
