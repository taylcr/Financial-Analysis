from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import yfinance as yf
import openai
import os
from bs4 import BeautifulSoup
import json
import re
import boto3
import webbrowser
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Load environment variables from .env file
load_dotenv()

# Define function to retrieve CIK from Claude
def get_cik_from_claude(ticker):
    bedrock_runtime = boto3.client(
        'bedrock-runtime',
        region_name=os.getenv('AWS_DEFAULT_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        aws_session_token=os.getenv('AWS_SESSION_TOKEN')
    )
    
    
    prompt = f"What is the Central Index Key (CIK) number for the company with the ticker symbol '{ticker}' from https://www.sec.gov/Archives/edgar? Please only give the 0000 followed by the CIK and say nothing more or less."

    kwargs = {
        "modelId": "anthropic.claude-3-haiku-20240307-v1:0",
        "contentType": "application/json",
        "accept": "application/json",
        "body": json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": prompt}]
        })
    }

    response = bedrock_runtime.invoke_model(**kwargs)
    body = json.loads(response.get('body').read())
    # print("get_cik_from_claude response body:", body)
    bodi= body.get('content', [{}])[0].get('text', '').strip()
    print("bodi:", bodi)
    return bodi

# Function to download and analyze SEC document
def download_and_analyze_sec_document(cik, year, form_type, isLink):
    url = f'https://data.sec.gov/submissions/CIK{cik}.json'
    headers = {'User-Agent': 'MyFinApp/1.0 (contact@mydomain.com)'}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception('Error fetching SEC data')

    data = response.json()
    filings = data.get("filings", {}).get("recent", {})

    for i, form in enumerate(filings.get("form", [])):
        if form == form_type and filings["filingDate"][i].startswith(str(year)):
            accession_number = filings["accessionNumber"][i].replace("-", "")
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number}/{filings['primaryDocument'][i]}"

            if isLink:
                webbrowser.open(filing_url)
            else:
            # Download HTML content
                filing_page = requests.get(filing_url, headers=headers)
                html_filename = f"{cik}_{form_type}_{year}.html"
                with open(html_filename, 'wb') as file:
                    file.write(filing_page.content)
                print(f"Downloaded HTML: {html_filename}")

                # Read HTML content for analysis
                with open(html_filename, 'r', encoding='utf-8') as file:
                    html_text = file.read()

                # Choose prompt based on form_type
                if form_type == "DEF 14A":
                       prompt = """Review this proxy statement to extract information on:
                        - Board of Directors composition and structure.
                        - Executive compensation details.
                        - Major shareholders and their influence.
                        - Governance practices and any proposals that impact policy."""
                
                elif form_type == "8-K":
                   prompt = """Examine this 8-K report to provide a summary of:
                        - Significant recent events (e.g., leadership changes, transactions).
                        - Any major financial updates or critical announcements.
                        - Immediate strategic implications for the company."""
                
                elif form_type == "10-K":
                    
                    prompt = """Provide a comprehensive analysis of the annual report focusing on:
                        - Key financial performance, with specific figures for principal assets and liabilities (e.g., Derivative Assets, Other Current and Noncurrent Assets, and Liabilities).
                        - Major highs and lows in recent years.
                        - Information on any borrowing for growth or issuance of new shares, with amounts where available.
                        - The companys ability to cover short-term liabilities based on its assets.
                        - Dividend performance versus capital gains focus.
                        - Whether the company is conserving cash for acquisitions, specifying which if applicable.
                        - Evidence of growth potential, supported by specific financial indicators.
                        - Changes in operating costs and their impact, especially if costs are rising without sales growth.
                        - Managements strategic objectives, revenue trends, risks, growth opportunities, and outlook.
                        Ensure that the analysis includes specific numbers and financial data where present in the text."""
                
                elif form_type == "10-Q":
                  
                     prompt = """Analyze this quarterly report to provide insights on:
                        - Short-term performance indicators.
                        - Any changes in costs or revenue, and implications for overall performance.
                        - Key updates on risks or market changes.
                        - Adjustments in financial guidance or forecasts if present."""
                
               
                else:
                    prompt = """Provide a high-level analysis of this filing, emphasizing:
                        - Key financial or strategic insights.
                        - Stakeholder implications.
                        - Any critical updates on operations or market positioning."""
                   # Load environment variables and configure AWS client
                load_dotenv()
                bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')

                # Call the AI model
                kwargs = {
                    "modelId": "anthropic.claude-3-haiku-20240307-v1:0",
                    "contentType": "application/json",
                    "accept": "application/json",
                    "body": json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 1000,
                        "messages": [{"role": "user", "content": prompt}]
                    })
                }

                response = bedrock_runtime.invoke_model(**kwargs)
                body = json.loads(response['body'].read())
                print("Analysis Result:", body)
                return body


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_stock_data', methods=['POST'])
def get_stock_data():
    try:
        data = request.get_json()
        ticker_symbol = data.get('ticker', '').upper()
        time_range = data.get('range', '1y')

        if not ticker_symbol:
            return jsonify({'error': 'Please provide a ticker symbol'}), 400

        range_mapping = {
            '5m': '5m',
            '1d': '1d',
            '1m': '1mo',
            '1y': '1y',
            '5y': '5y',
            'all': 'max'
        }
        
        period = range_mapping.get(time_range, '1y')
        interval = '5m' if time_range == '5m' else '1d'

        stock = yf.Ticker(ticker_symbol)
        stock_info = stock.history(period=period, interval=interval)

        if stock_info.empty:
            return jsonify({'error': 'Invalid ticker symbol or no data found'}), 404

        financials = stock.quarterly_financials
        current_revenue = financials.at['Total Revenue', financials.columns[0]] if 'Total Revenue' in financials.index else None
        previous_revenue = financials.at['Total Revenue', financials.columns[4]] if 'Total Revenue' in financials.index and len(financials.columns) > 4 else None

        response_data = {
            'ticker': ticker_symbol,
            'price': stock_info['Close'].tolist(),
            'dates': stock_info.index.strftime("%Y-%m-%d %H:%M:%S").tolist(),
            'current_revenue': current_revenue,
            'previous_revenue': previous_revenue
        }
        
        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': f'Error fetching stock data: {str(e)}'}), 500

@app.route('/get_financial_indicators', methods=['POST'])
def get_financial_indicators():
    try:
        data = request.get_json()
        ticker_symbol = data.get('ticker', '').upper()

        if not ticker_symbol:
            return jsonify({'error': 'Please provide a ticker symbol'}), 400
        
        stock = yf.Ticker(ticker_symbol)
        info = stock.info

        response_data = {
            'revenue': info.get('totalRevenue'),
            'gross_margin': info.get('grossMargins'),
            'free_cash_flow': info.get('freeCashflow'),
            'net_debt': info.get('totalDebt') - info.get('cash') if info.get('totalDebt') and info.get('cash') else None,
            'ebitda': info.get('ebitda'),
            'eps': info.get('trailingEps')
        }

        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': f'Error fetching financial indicators: {str(e)}'}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        conversation_history = data.get('conversationHistory', '')

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Send the accumulated conversation history as context
        messages = [
            {"role": "user", "content": conversation_history + f"\nUser: {user_message}"}
        ]

        # AWS Bedrock request setup
        bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_DEFAULT_REGION'))
        kwargs = {
            "modelId": "anthropic.claude-3-haiku-20240307-v1:0",
            "contentType": "application/json",
            "accept": "application/json",
            "body": json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 80,
                "messages": messages
            })
        }

        response = bedrock_runtime.invoke_model(**kwargs)
        body = json.loads(response['body'].read())
        assistant_response = body.get('content', [{}])[0].get('text', '').strip()

        # Respond with the assistant's message
        return jsonify({'summary': assistant_response})

    except Exception as e:
        return jsonify({'error': f'Error processing message: {str(e)}'}), 500

@app.route('/analyze_sec_report', methods=['POST'])



def analyze_sec_report():
    try:
        data = request.get_json()
        ticker = data.get('ticker')
        year = data.get('year')
        form_type = data.get('formType')
        open_link = data.get('openLink', True)

        if not all([ticker, year, form_type]):
            return jsonify({'error': 'Missing required parameters'}), 400

        cik = get_cik_from_claude(ticker)
        if not cik:
            return jsonify({'error': 'Could not find CIK for the given ticker'}), 404

        result = download_and_analyze_sec_document(cik, year, form_type, open_link)
        
        # Structure response based on AI's content
        analysis_text = result['content'][0]['text']  # Retrieve text part from response
        
        print("RESULT--->:", analysis_text)

        
        return jsonify({'analysis': analysis_text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
# Run the app
if __name__ == '__main__':
    app.run(debug=True)
