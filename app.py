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
        ticker_symbol = data.get('ticker', '').upper()
        time_range = data.get('range', '1y')  # Default to 1 year

        if not ticker_symbol:
            return jsonify({'error': 'Please provide a ticker symbol'}), 400

        # Convert time range to yfinance period parameter
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

        # Retrieve stock data
        stock = yf.Ticker(ticker_symbol)
        stock_info = stock.history(period=period, interval=interval)

        if stock_info.empty:
            return jsonify({'error': 'Invalid ticker symbol or no data found'}), 404

        # For revenue calculation, get quarterly financials
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

        system_message = """You are a helpful stock market assistant. You can:
        1. Explain stock market terms and concepts
        2. Provide general investment advice and strategies
        3. Analyze market trends
        4. Answer questions about stocks and trading
        Keep responses concise and informative."""

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.7,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        assistant_response = response.choices[0].message['content']
        
        return jsonify({'summary': assistant_response})

    except openai.error.OpenAIError as e:
        return jsonify({'error': f'OpenAI API error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error processing message: {str(e)}'}), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True)