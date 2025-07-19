# 🚀 Trading Bot Dashboard

A simple, colorful trading bot simulation with a beautiful web interface!

## Features

- 💰 **Real-time balance tracking** - Watch your account balance and portfolio value
- 📈 **Live price simulation** - Simulated stock prices for popular stocks (AAPL, GOOGL, TSLA, MSFT, AMZN)
- 🤖 **Automated trading** - Bot automatically buys on dips and sells on rises
- 💼 **Manual trading** - Buy and sell stocks manually through the interface
- 📊 **Trading history** - Track all your trades with timestamps
- 🎨 **Beautiful UI** - Colorful, modern interface with gradients and animations

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the trading bot:**
   ```bash
   python trading_bot.py
   ```

3. **Open your browser:**
   Navigate to `http://localhost:8080`

### Deploy to Heroku

1. **Install Heroku CLI** (if not already installed):
   ```bash
   # macOS
   brew install heroku/brew/heroku
   
   # Windows
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login to Heroku:**
   ```bash
   heroku login
   ```

3. **Create a new Heroku app:**
   ```bash
   heroku create your-trading-bot-name
   ```

4. **Deploy to Heroku:**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

5. **Open your deployed app:**
   ```bash
   heroku open
   ```

**Note:** Replace `your-trading-bot-name` with a unique name for your app.

## How to Use

### Starting the Bot
- Click the "Start Bot" button to begin automated trading
- The bot will automatically buy stocks when prices drop more than 1%
- It will sell stocks when prices rise more than 1%

### Manual Trading
- Select a stock symbol from the dropdown
- Enter the quantity you want to trade
- Click "Buy" or "Sell" to execute trades

### Monitoring
- Watch your account balance and portfolio value in real-time
- View live stock prices that update every 2 seconds
- Check the trading history to see all your trades

## Trading Strategy

The bot uses a simple strategy:
- **Buy Signal**: When a stock price drops more than 1% from the previous price
- **Sell Signal**: When a stock price rises more than 1% from the previous price
- **Position Sizing**: Buys up to $1000 worth of stock per trade, sells up to 5 shares

## Technical Details

- **Backend**: Python Flask server
- **Frontend**: HTML/CSS/JavaScript with modern design
- **Port**: 8080 (configurable in the code)
- **Update Frequency**: Every 2 seconds
- **Price Simulation**: Random movements between -2% and +2%

## Files

- `trading_bot.py` - Main Flask application
- `templates/index.html` - Web interface
- `requirements.txt` - Python dependencies
- `README.md` - This file

## Disclaimer

This is a **simulation** for educational purposes only. No real money is involved, and the trading strategies are simplified for demonstration. Do not use this for actual trading without significant modifications and proper risk management.

---

Enjoy trading! 🎉 