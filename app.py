from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import yfinance as yf
import openai
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Set your OpenAI API key
openai.api_key = "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"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_stock_data', methods=['POST'])
def get_stock_data():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
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

        # Create a system message for the stock assistant
        system_message = """You are a helpful stock market assistant. You can:
        1. Explain stock market terms and concepts
        2. Provide general investment advice and strategies
        3. Analyze market trends
        4. Answer questions about stocks and trading
        Keep responses concise and informative."""

        # Create the messages array for the API call
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]

        # Make the API call to OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.7,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        # Extract the assistant's response
        assistant_response = response.choices[0].message['content']
        
        return jsonify({'summary': assistant_response})

    except openai.error.OpenAIError as e:
        # Handle OpenAI-specific errors
        error_message = f"OpenAI API error: {str(e)}"
        return jsonify({'error': error_message}), 500
    except Exception as e:
        # Handle other errors
        return jsonify({'error': f'Error processing message: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)