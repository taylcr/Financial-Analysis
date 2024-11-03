import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator

# List of companies (tickers) for comparison
companies = ['AAPL', 'MSFT', 'GOOG', 'AMZN']
start_date = '2022-01-01'
end_date = datetime.today().strftime('%Y-%m-%d')

# Fetch adjusted close data
data = yf.download(companies, start=start_date, end=end_date)['Adj Close']

# Normalize prices for comparison
normalized_data = data / data.iloc[0] * 100

# Calculate 20-day Moving Average and RSI for each company
technical_indicators = {}
for company in companies:
    stock_data = data[company].dropna()
    sma_20 = SMAIndicator(stock_data, window=20).sma_indicator()
    rsi_14 = RSIIndicator(stock_data, window=14).rsi()
    technical_indicators[company] = {'SMA_20': sma_20, 'RSI_14': rsi_14}

# Retrieve Fundamental Data (Revenue, Net Income, EPS) using yfinance
fundamentals = {}
for company in companies:
    stock_info = yf.Ticker(company).info
    fundamentals[company] = {
        'Revenue': stock_info.get('totalRevenue'),
        'Net Income': stock_info.get('netIncomeToCommon'),
        'EPS': stock_info.get('trailingEps')
    }

# Plotting
fig, axs = plt.subplots(3, 1, figsize=(14, 18), gridspec_kw={'height_ratios': [3, 1, 1]})

# Plot normalized price performance
for company in companies:
    axs[0].plot(normalized_data.index, normalized_data[company], label=company)
axs[0].set_title('Normalized Price Comparison')
axs[0].set_ylabel('Normalized Price (Starting at 100)')
axs[0].legend()

# Plot 20-day SMA on the price performance chart
for company in companies:
    axs[0].plot(technical_indicators[company]['SMA_20'], linestyle='--', label=f'{company} 20-day SMA')

# Plot RSI for each company
for company in companies:
    axs[1].plot(technical_indicators[company]['RSI_14'], label=f'{company} RSI')
axs[1].set_title('14-day RSI')
axs[1].set_ylabel('RSI')
axs[1].axhline(70, color='red', linestyle='--')  # Overbought level
axs[1].axhline(30, color='green', linestyle='--')  # Oversold level
axs[1].legend()

# Display fundamental metrics as a table
fundamentals_df = pd.DataFrame(fundamentals).T
axs[2].axis('off')
table = axs[2].table(cellText=fundamentals_df.values, colLabels=fundamentals_df.columns, rowLabels=fundamentals_df.index, loc='center')
table.scale(1, 2)  # Adjust table size for readability
axs[2].set_title('Fundamental Metrics Comparison (Revenue, Net Income, EPS)')

plt.tight_layout()
plt.show()
