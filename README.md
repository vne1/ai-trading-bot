# 🤖 AI Trading Bot with Sentiment Analysis

A sophisticated AI-powered trading bot that combines technical analysis with sentiment analysis to make intelligent trading decisions in real-time.

## ✨ Features

### 🎯 Core Trading Features
- **Real-time Market Data**: Live price feeds from Yahoo Finance API
- **Technical Analysis**: RSI, SMA, volume analysis, and trend detection
- **Automated Trading**: Smart buy/sell decisions based on multiple indicators
- **Portfolio Management**: Real-time balance and position tracking
- **Risk Management**: Configurable trading limits and stop-losses

### 🧠 Sentiment Analysis Integration
- **Multi-source Sentiment**: Reddit (r/wallstreetbets), News API, and social media
- **TextBlob NLP**: Natural language processing for sentiment scoring
- **Weighted Analysis**: Combines sentiment from multiple sources
- **Real-time Updates**: Sentiment data refreshed every 15 minutes
- **Trading Integration**: Sentiment signals influence buy/sell decisions

### 🌐 Web Dashboard
- **Real-time UI**: Live updates of portfolio, prices, and sentiment
- **Interactive Charts**: Price charts with trade markers
- **Sentiment Dashboard**: Color-coded sentiment scores and breakdown
- **Trading Controls**: Manual trade execution and bot toggle
- **Responsive Design**: Works on desktop and mobile devices

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/vne1/ai-trading-bot.git
   cd ai-trading-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the trading bot**
   ```bash
   python3 trading_bot.py
   ```

4. **Access the dashboard**
   - Open your browser to `http://localhost:5239`
   - The bot will start with $10,000 initial balance

## 📊 API Endpoints

### Core Endpoints
- `GET /api/status` - Get current bot status, portfolio, and sentiment data
- `POST /api/trade` - Execute manual trades
- `POST /api/toggle_bot` - Start/stop automated trading
- `GET /api/chart/<symbol>` - Get price chart data with trade markers

### Sentiment Endpoints
- `GET /api/sentiment/<symbol>` - Get sentiment analysis for specific symbol
- Sentiment data included in `/api/status` response

## 🎛️ Configuration

### Trading Parameters
- **Initial Balance**: $10,000 (configurable)
- **Trade Size**: 1-5 shares per trade
- **Update Frequency**: Every 30 seconds
- **Sentiment Update**: Every 15 minutes

### Supported Symbols
- **Tech Stocks**: AAPL, GOOGL, MSFT, TSLA, NVDA, META, AMZN, NFLX
- **Easy to add**: Modify `SYMBOLS` list in `trading_bot.py`

### Sentiment Sources
- **Reddit**: r/wallstreetbets posts
- **News API**: Financial news articles
- **Social Media**: Simulated sentiment data
- **Weights**: Configurable source importance

## 🔧 Customization

### Adding New Symbols
```python
SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA', 'META', 'AMZN', 'NFLX', 'YOUR_SYMBOL']
```

### Modifying Trading Strategy
Edit the `auto_trade()` method in `trading_bot.py` to implement your own strategy.

### Adjusting Sentiment Weights
```python
SENTIMENT_WEIGHTS = {
    'reddit': 0.4,
    'news': 0.4,
    'social': 0.2
}
```

## 📈 Trading Strategy

### Technical Indicators
- **RSI (Relative Strength Index)**: Oversold/overbought conditions
- **SMA (Simple Moving Average)**: Trend direction
- **Volume Analysis**: Market participation
- **Price Action**: Support/resistance levels

### Sentiment Integration
- **Positive Sentiment**: Increases buy confidence
- **Negative Sentiment**: Triggers sell signals
- **Neutral Sentiment**: Relies on technical analysis
- **Confidence Levels**: 0.6+ for strong signals

### Risk Management
- **Position Sizing**: Limited shares per trade
- **Diversification**: Multiple symbols
- **Stop Loss**: Automatic loss prevention
- **Market Hours**: Only trades during market hours

## 🛠️ Development

### Project Structure
```
ai-trading-bot/
├── trading_bot.py          # Main application
├── templates/
│   └── index.html         # Web dashboard
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore           # Git ignore rules
├── Procfile             # Heroku deployment
├── railway.json         # Railway deployment
└── runtime.txt          # Python version
```

### Key Components
- **TradingBot Class**: Core trading logic and portfolio management
- **Flask App**: Web API and dashboard server
- **Sentiment Analysis**: Multi-source sentiment processing
- **Real-time Updates**: Background threading for data updates

## 🚀 Deployment

### Local Development
```bash
python3 trading_bot.py
```

### Cloud Deployment
The project includes configuration for:
- **Heroku**: Use `Procfile` and `requirements.txt`
- **Railway**: Use `railway.json` configuration
- **Other Platforms**: Standard Python web app deployment

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## ⚠️ Disclaimer

This trading bot is for educational and demonstration purposes only. Trading involves risk, and past performance does not guarantee future results. Always do your own research and consider consulting with a financial advisor before making investment decisions.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you have questions or need help:
1. Check the [Issues](https://github.com/vne1/ai-trading-bot/issues) page
2. Create a new issue for bugs or feature requests
3. Review the code comments for implementation details

---

**Happy Trading! 📈💰** 