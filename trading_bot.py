from flask import Flask, render_template, jsonify, request
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.utils
import json
import time
import threading
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# Trading bot state
class TradingBot:
    def __init__(self):
        self.balance = 10000.0
        self.portfolio = {}
        self.trading_history = []
        self.is_running = False
        self.symbols = ['AAPL', 'GOOGL', 'TSLA', 'MSFT', 'AMZN', 'NVDA', 'META', 'NFLX']
        self.current_prices = {}
        self.price_history = {}
        self.technical_indicators = {}
        self.last_update = {}
        
        # Initialize price data
        self.initialize_prices()
    
    def initialize_prices(self):
        """Initialize current prices and history for all symbols"""
        for symbol in self.symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                self.current_prices[symbol] = info.get('regularMarketPrice', 100.0)
                self.price_history[symbol] = []
                self.last_update[symbol] = datetime.now()
                self.technical_indicators[symbol] = {
                    'sma_20': 0,
                    'rsi': 50,
                    'volume': 0
                }
            except Exception as e:
                print(f"Error initializing {symbol}: {e}")
                self.current_prices[symbol] = 100.0
                self.price_history[symbol] = []
                self.last_update[symbol] = datetime.now()

    def get_real_price(self, symbol):
        """Get real-time price from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info.get('regularMarketPrice', self.current_prices.get(symbol, 100.0))
        except Exception as e:
            print(f"Error getting price for {symbol}: {e}")
            return self.current_prices.get(symbol, 100.0)

    def get_historical_data(self, symbol, period='1d', interval='5m'):
        """Get historical data for technical analysis"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            return hist
        except Exception as e:
            print(f"Error getting historical data for {symbol}: {e}")
            return pd.DataFrame()

    def calculate_technical_indicators(self, symbol):
        """Calculate technical indicators"""
        try:
            hist = self.get_historical_data(symbol, period='5d', interval='5m')
            if hist.empty:
                return
            
            # Simple Moving Average (20-period)
            if len(hist) >= 20:
                self.technical_indicators[symbol]['sma_20'] = hist['Close'].tail(20).mean()
            
            # RSI (14-period)
            if len(hist) >= 14:
                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                self.technical_indicators[symbol]['rsi'] = rsi.iloc[-1]
            
            # Volume
            if len(hist) > 0:
                self.technical_indicators[symbol]['volume'] = hist['Volume'].iloc[-1]
                
        except Exception as e:
            print(f"Error calculating indicators for {symbol}: {e}")

    def update_prices(self):
        """Update prices with real market data"""
        for symbol in self.symbols:
            try:
                # Get real price
                real_price = self.get_real_price(symbol)
                old_price = self.current_prices.get(symbol, real_price)
                
                # Update current price
                self.current_prices[symbol] = real_price
                
                # Add to price history
                self.price_history[symbol].append({
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'price': real_price,
                    'change': real_price - old_price,
                    'change_pct': ((real_price - old_price) / old_price * 100) if old_price > 0 else 0
                })
                
                # Keep only last 100 data points
                if len(self.price_history[symbol]) > 100:
                    self.price_history[symbol] = self.price_history[symbol][-100:]
                
                # Update technical indicators every 5 minutes
                if (datetime.now() - self.last_update[symbol]).seconds > 300:
                    self.calculate_technical_indicators(symbol)
                    self.last_update[symbol] = datetime.now()
                    
            except Exception as e:
                print(f"Error updating {symbol}: {e}")

    def buy_stock(self, symbol, quantity):
        """Buy stocks"""
        if symbol not in self.current_prices:
            return False, "Invalid symbol"
        
        cost = self.current_prices[symbol] * quantity
        if cost > self.balance:
            return False, "Insufficient funds"
        
        self.balance -= cost
        if symbol in self.portfolio:
            self.portfolio[symbol] += quantity
        else:
            self.portfolio[symbol] = quantity
        
        self.trading_history.append({
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': 'BUY',
            'symbol': symbol,
            'quantity': quantity,
            'price': self.current_prices[symbol],
            'total': cost,
            'balance_after': self.balance
        })
        
        return True, f"Bought {quantity} shares of {symbol} at ${self.current_prices[symbol]:.2f}"

    def sell_stock(self, symbol, quantity):
        """Sell stocks"""
        if symbol not in self.portfolio or self.portfolio[symbol] < quantity:
            return False, "Insufficient shares"
        
        revenue = self.current_prices[symbol] * quantity
        self.balance += revenue
        self.portfolio[symbol] -= quantity
        
        if self.portfolio[symbol] == 0:
            del self.portfolio[symbol]
        
        self.trading_history.append({
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': 'SELL',
            'symbol': symbol,
            'quantity': quantity,
            'price': self.current_prices[symbol],
            'total': revenue,
            'balance_after': self.balance
        })
        
        return True, f"Sold {quantity} shares of {symbol} at ${self.current_prices[symbol]:.2f}"

    def auto_trade(self):
        """Enhanced automated trading strategy using technical indicators"""
        if not self.is_running:
            return
        
        for symbol in self.symbols:
            try:
                if len(self.price_history[symbol]) < 2:
                    continue
                
                current_price = self.current_prices[symbol]
                prev_price = self.price_history[symbol][-2]['price']
                change_pct = (current_price - prev_price) / prev_price
                
                # Get technical indicators
                rsi = self.technical_indicators[symbol]['rsi']
                sma_20 = self.technical_indicators[symbol]['sma_20']
                
                # Enhanced buy signal: RSI oversold + price drop + above SMA
                if (rsi < 30 and change_pct < -0.005 and 
                    current_price > sma_20 and self.balance > 1000):
                    quantity = int(1000 / current_price)
                    if quantity > 0:
                        self.buy_stock(symbol, quantity)
                
                # Enhanced sell signal: RSI overbought + price rise + below SMA
                elif (rsi > 70 and change_pct > 0.005 and 
                      current_price < sma_20 and symbol in self.portfolio):
                    quantity = min(self.portfolio[symbol], 5)
                    if quantity > 0:
                        self.sell_stock(symbol, quantity)
                        
            except Exception as e:
                print(f"Error in auto-trade for {symbol}: {e}")

    def generate_chart_data(self, symbol):
        """Generate chart data for a symbol"""
        try:
            if not self.price_history[symbol]:
                return None
            
            times = [point['time'] for point in self.price_history[symbol]]
            prices = [point['price'] for point in self.price_history[symbol]]
            changes = [point['change_pct'] for point in self.price_history[symbol]]
            
            # Create candlestick chart data
            chart_data = {
                'times': times,
                'prices': prices,
                'changes': changes,
                'current_price': self.current_prices[symbol],
                'rsi': self.technical_indicators[symbol]['rsi'],
                'sma_20': self.technical_indicators[symbol]['sma_20'],
                'volume': self.technical_indicators[symbol]['volume']
            }
            
            return chart_data
            
        except Exception as e:
            print(f"Error generating chart data for {symbol}: {e}")
            return None

# Initialize trading bot
bot = TradingBot()

def price_update_loop():
    """Background thread for updating prices and auto-trading"""
    while True:
        try:
            if bot.is_running:
                bot.update_prices()
                bot.auto_trade()
            time.sleep(30)  # Update every 30 seconds for real data
        except Exception as e:
            print(f"Error in price update loop: {e}")
            time.sleep(60)  # Wait longer on error

# Start background thread
price_thread = threading.Thread(target=price_update_loop, daemon=True)
price_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    portfolio_value = sum(bot.portfolio.get(symbol, 0) * bot.current_prices.get(symbol, 0) 
                         for symbol in bot.current_prices)
    total_value = bot.balance + portfolio_value
    
    return jsonify({
        'balance': round(bot.balance, 2),
        'portfolio': bot.portfolio,
        'portfolio_value': round(portfolio_value, 2),
        'total_value': round(total_value, 2),
        'prices': bot.current_prices,
        'price_history': bot.price_history,
        'technical_indicators': bot.technical_indicators,
        'trading_history': bot.trading_history[-10:],
        'is_running': bot.is_running,
        'symbols': bot.symbols
    })

@app.route('/api/chart/<symbol>')
def get_chart_data(symbol):
    chart_data = bot.generate_chart_data(symbol)
    if chart_data:
        return jsonify(chart_data)
    else:
        return jsonify({'error': 'No data available'})

@app.route('/api/trade', methods=['POST'])
def trade():
    data = request.json or {}
    action = data.get('action')
    symbol = data.get('symbol')
    quantity = int(data.get('quantity', 1))
    
    if action == 'buy':
        success, message = bot.buy_stock(symbol, quantity)
    elif action == 'sell':
        success, message = bot.sell_stock(symbol, quantity)
    else:
        return jsonify({'success': False, 'message': 'Invalid action'})
    
    return jsonify({'success': success, 'message': message})

@app.route('/api/toggle_bot', methods=['POST'])
def toggle_bot():
    bot.is_running = not bot.is_running
    return jsonify({'is_running': bot.is_running})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Starting Trading Bot with Real Market Data on port {port}")
    print("💡 The bot will automatically trade based on real market movements")
    print("📊 Using Yahoo Finance API for live data")
    app.run(host='0.0.0.0', port=port, debug=False) 