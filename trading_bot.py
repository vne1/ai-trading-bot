from flask import Flask, render_template, jsonify, request
import random
import time
import threading
from datetime import datetime
import json

app = Flask(__name__)

# Trading bot state
class TradingBot:
    def __init__(self):
        self.balance = 10000.0
        self.portfolio = {}
        self.trading_history = []
        self.is_running = False
        self.current_prices = {
            'AAPL': 150.0,
            'GOOGL': 2800.0,
            'TSLA': 250.0,
            'MSFT': 300.0,
            'AMZN': 3300.0
        }
        self.price_history = {symbol: [] for symbol in self.current_prices.keys()}

    def update_prices(self):
        """Simulate price movements"""
        for symbol in self.current_prices:
            # Random price movement between -2% and +2%
            change = random.uniform(-0.02, 0.02)
            self.current_prices[symbol] *= (1 + change)
            self.current_prices[symbol] = round(self.current_prices[symbol], 2)
            
            # Keep price history (last 50 points)
            self.price_history[symbol].append({
                'time': datetime.now().strftime('%H:%M:%S'),
                'price': self.current_prices[symbol]
            })
            if len(self.price_history[symbol]) > 50:
                self.price_history[symbol].pop(0)

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
            'total': cost
        })
        
        return True, f"Bought {quantity} shares of {symbol} at ${self.current_prices[symbol]}"

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
            'total': revenue
        })
        
        return True, f"Sold {quantity} shares of {symbol} at ${self.current_prices[symbol]}"

    def auto_trade(self):
        """Simple automated trading strategy"""
        if not self.is_running:
            return
        
        for symbol in self.current_prices:
            # Simple strategy: buy if price dropped more than 1%, sell if it rose more than 1%
            if len(self.price_history[symbol]) < 2:
                continue
            
            current_price = self.current_prices[symbol]
            prev_price = self.price_history[symbol][-2]['price']
            change_pct = (current_price - prev_price) / prev_price
            
            if change_pct < -0.01 and self.balance > 1000:  # Buy on dip
                quantity = int(1000 / current_price)
                if quantity > 0:
                    self.buy_stock(symbol, quantity)
            
            elif change_pct > 0.01 and symbol in self.portfolio:  # Sell on rise
                quantity = min(self.portfolio[symbol], 5)  # Sell up to 5 shares
                if quantity > 0:
                    self.sell_stock(symbol, quantity)

# Initialize trading bot
bot = TradingBot()

def price_update_loop():
    """Background thread for updating prices and auto-trading"""
    while True:
        if bot.is_running:
            bot.update_prices()
            bot.auto_trade()
        time.sleep(2)

# Start background thread
price_thread = threading.Thread(target=price_update_loop, daemon=True)
price_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    portfolio_value = sum(bot.portfolio.get(symbol, 0) * bot.current_prices[symbol] 
                         for symbol in bot.current_prices)
    total_value = bot.balance + portfolio_value
    
    return jsonify({
        'balance': round(bot.balance, 2),
        'portfolio': bot.portfolio,
        'portfolio_value': round(portfolio_value, 2),
        'total_value': round(total_value, 2),
        'prices': bot.current_prices,
        'price_history': bot.price_history,
        'trading_history': bot.trading_history[-10:],  # Last 10 trades
        'is_running': bot.is_running
    })

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
    print(f"🚀 Starting Trading Bot on port {port}")
    print("💡 The bot will automatically trade based on price movements")
    app.run(host='0.0.0.0', port=port, debug=False) 