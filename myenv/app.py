from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import yfinance as yf
import boto3
import json
import pandas as pd
from io import StringIO
from dotenv import load_dotenv
import threading
from crawler import run_crawler
from reddit_scrapper import run_reddit_scraper

app = Flask(__name__)
CORS(app)

# Load environment variables from .env file
load_dotenv()

# Initialize Bedrock runtime client
bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-west-2"
)

# Define the Get_opinion function
def Get_opinion(input):
    s3 = boto3.client('s3')
    bucket_name = "webscrapper2"
    data_file_key = "data.csv"
    urls_content_file_key = "urls_contents.csv"

    def read_csv_from_s3(bucket, key):
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        return pd.read_csv(StringIO(content))

    data_df = read_csv_from_s3(bucket_name, data_file_key)
    urls_content_df = read_csv_from_s3(bucket_name, urls_content_file_key)

    mentions_data = data_df[data_df.apply(lambda row: row.astype(str).str.contains(input, case=False).any(), axis=1)]
    mentions_urls_content = urls_content_df[urls_content_df.apply(lambda row: row.astype(str).str.contains(input, case=False).any(), axis=1)]

    insights = "\n".join(mentions_data.astype(str).apply(" | ".join, axis=1).values.tolist())
    insights += "\n" + "\n".join(mentions_urls_content.astype(str).apply(" | ".join, axis=1).values.tolist())

    prompt = f"Based on the following information about {input}, what do people think about it?\n\n{insights}"

    kwargs = {
        "modelId": "anthropic.claude-3-sonnet-20240229-v1:0",
        "contentType": "application/json",
        "accept": "application/json",
        "body": json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 200,
            "temperature": 1,
            "top_p": 0.999,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
    }

    response = bedrock_runtime.invoke_model(**kwargs)
    response_body = response['body'].read().decode('utf-8')
    response_data = json.loads(response_body)
    return response_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webscraper')
def webscraper_page():
    return render_template('webscraper.html')

@app.route('/get_stock_data', methods=['POST'])
def get_stock_data():
    try:
        data = request.get_json()
        ticker_symbol = data.get('ticker', '').upper()
        
        if not ticker_symbol:
            return jsonify({'error': 'Please provide a ticker symbol'}), 400
        
        # Retrieve stock data
        stock = yf.Ticker(ticker_symbol)
        stock_info = stock.history(period="1mo")
        
        if stock_info.empty:
            return jsonify({'error': 'Invalid ticker symbol or no data found'}), 404
        
        response_data = {
            'ticker': ticker_symbol,
            'price': stock_info['Close'].tolist(),
            'dates': stock_info.index.strftime("%Y-%m-%d").tolist()
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
        
        # Retrieve financial indicators
        stock = yf.Ticker(ticker_symbol)
        info = stock.info

        # Collect the financial indicators
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

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Prepare the prompt and request parameters for Claude via Bedrock
        prompt = f"You are a helpful stock market assistant. Answer the user's query:\nUser: {user_message}\nAssistant:"
        kwargs = {
            "modelId": "anthropic.claude-3-sonnet-20240229-v1:0",
            "contentType": "application/json",
            "accept": "application/json",
            "body": json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 200,
                "top_k": 250,
                "stop_sequences": [],
                "temperature": 1,
                "top_p": 0.999,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            })
        }

        # Call the Claude model
        response = bedrock_runtime.invoke_model(**kwargs)
        response_body = response['body'].read().decode('utf-8')
        
        # Parse JSON response
        response_data = json.loads(response_body)
        
        # Extract the assistant's response from the content structure
        if "content" in response_data and response_data["content"]:
            assistant_response = response_data["content"][0]["text"]
        else:
            assistant_response = "No response received"
        
        return jsonify({'summary': assistant_response})

    except Exception as e:
        return jsonify({'error': f'Error processing message: {str(e)}'}), 500

@app.route('/start_scraping_and_analyze', methods=['POST'])
def start_scraping_and_analyze():
    data = request.get_json()
    query = data.get("query")
    
    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Start the scrapers in threads
    crawler_thread = threading.Thread(target=run_crawler, args=(query,))
    reddit_thread = threading.Thread(target=run_reddit_scraper)
    crawler_thread.start()
    reddit_thread.start()

    # Wait for both threads to complete
    crawler_thread.join()
    reddit_thread.join()

    # Once scraping is complete, call Get_opinion to analyze the data
    result = Get_opinion(query)

    # Extract and return the summary
    if "content" in result and isinstance(result["content"], list) and result["content"]:
        summary = result["content"][0].get("text", "No relevant information found.")
    else:
        summary = "Error processing request."

    return jsonify({"summary": summary})

if __name__ == '__main__':
    app.run(debug=True)
