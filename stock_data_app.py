from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)

# Simple CORS configuration
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    return render_template('stock_data_viewer.html')

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
        stock_info = stock.history(period="1mo")  # Get the last month of data
        
        if stock_info.empty:
            return jsonify({'error': 'Invalid ticker symbol or no data found'}), 404
        
        # Return stock data as JSON
        response_data = {
            'ticker': ticker_symbol,
            'price': stock_info['Close'].tolist(),
            'dates': stock_info.index.strftime("%Y-%m-%d").tolist()
        }
        return jsonify(response_data)
    
    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error
        return jsonify({'error': f'Error fetching stock data: {str(e)}'}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    message = data.get('message')

    try:
        # Process the message and generate a response
        response = process_message(message)
        return jsonify({'summary': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_message(message):
    # Implement your chatbot logic here
    # You can use the OpenAI API or any other method to generate responses
    # For simplicity, this example just echoes the user's message
    return f"You said: {message}"

if __name__ == '__main__':
    app.run(debug=True)