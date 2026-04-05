import yfinance as yf
import time

# Step 1: Get inputs from user
symbol = input("Enter stock symbol (e.g. AAPL, TSLA): ").upper()
target_price = float(input("Enter your target price: "))

print(f"\nMonitoring {symbol}... Press Ctrl+C to stop.\n")

# Step 2: Keep checking the price in a loop
while True:
    # Step 3: Fetch current stock data
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")

    if data.empty:
        print("Could not fetch data. Check the stock symbol.")
        break

    # Step 4: Get the latest closing price
    current_price = data["Close"].iloc[-1]
    print(f"{symbol} Current Price: ${current_price:.2f} | Target: ${target_price:.2f}")

    # Step 5: Check if target is reached
    if current_price >= target_price:
        print(f"\n🚨 ALERT! {symbol} has reached ${current_price:.2f} — your target of ${target_price:.2f}!")
        break

    # Wait 60 seconds before checking again
    time.sleep(60)