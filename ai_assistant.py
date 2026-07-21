"""
AI Assistant - Rule-based chatbot for user questions
Answers common questions about Trade With AI, market hours, features, etc.
"""
import re
from datetime import datetime


class AIAssistant:
    """Rule-based assistant for Trade With AI"""
    
    def __init__(self):
        self.knowledge = self._build_knowledge_base()
    
    def _build_knowledge_base(self) -> dict:
        """Build knowledge base for common questions"""
        return {
            "market_hours": {
                "patterns": [r"market.*open", r"market.*close", r"trading hours", r"when can i trade", r"market status"],
                "answer": "US markets (NYSE/NASDAQ) are open Monday-Friday, 9:30 AM - 4:00 PM ET. Currently the market is {market_status}. However, the app works 24/7 — you can paper trade anytime using the latest available prices. Real-time price movement will resume when markets open."
            },
            "virtual_cash": {
                "patterns": [r"virtual cash", r"fake money", r"starting balance", r"how much.*start", r"\$100k", r"\$100,000"],
                "answer": "You start with $100,000 in virtual cash. This is simulated capital — there's no real money at risk. You use it to practice trading, test strategies, and experience the platform's AI signals without any financial exposure."
            },
            "ai_models": {
                "patterns": [r"how does.*ai work", r"what models", r"machine learning", r"ai.*accuracy", r"ai.*reliable"],
                "answer": "Trade With AI uses an ensemble of three models: Random Forest (pattern recognition), Gradient Boosting (sequential learning), and Logistic Regression (probability calibration). They work in consensus — a trade only executes when all three models agree with high confidence. This is the same approach used in institutional quantitative trading."
            },
            "trial": {
                "patterns": [r"free trial", r"how long", r"trial.*days", r"do i need.*register", r"5 day"],
                "answer": "Your first day is completely free with no registration required. Starting day 2, you'll need to register (just name + email — no credit card) to continue your 5-day trial. After day 5, you can subscribe to AI Signals for $9/week or upgrade to real-money trading for $99 (discounted from $120 for early adopters)."
            },
            "real_money": {
                "patterns": [r"real money", r"live trading", r"actual money", r"sec compliant", r"broker"],
                "answer": "Real-money trading is available after a one-time $99 onboarding fee (discounted from $120 for early adopters). This includes SEC-compliant setup, broker integration, and identity verification. After that, the platform takes 10% of your bi-weekly gains — no subscription fees. You only pay when you profit."
            },
            "features": {
                "patterns": [r"what can i do", r"features", r"capabilities", r"what.*included"],
                "answer": "You get: real-time market data for all US stocks, AI-powered buy/sell signals, technical analysis (RSI, MACD, Bollinger Bands), portfolio tracking with P/L calculations, automated trading with smart position sizing, backtesting with 5 years of historical data, and a full trade history. All on $100K of virtual cash."
            },
            "safety": {
                "patterns": [r"is.*safe", r"is this a scam", r"can i lose money", r"risk"],
                "answer": "Paper trading is completely risk-free — you're trading with virtual cash, so you cannot lose real money. The platform is for education and strategy testing. If you choose real-money mode later, you go through SEC-compliant onboarding with a regulated broker. Past performance does not guarantee future results."
            },
            "pricing": {
                "patterns": [r"how much", r"cost", r"price", r"subscription"],
                "answer": "After your 5-day free trial: AI Signals subscription is $9/week or $36/month. Investment Newsletter is $19/month. Real-money trading requires a one-time $99 onboarding (discounted from $120) plus 10% of bi-weekly gains when you profit. No subscription fees for real-money mode."
            },
            "registration": {
                "patterns": [r"how.*register", r"do i need.*sign up", r"create account", r"register"],
                "answer": "Registration is simple: just your name and email address. No credit card, no phone verification, no lengthy forms. After day 1, you'll be prompted to register to continue your trial. You can also browse public pages (Backtest Results, Pricing) without registering."
            },
            "auto_trading": {
                "patterns": [r"auto.*trade", r"automated", r"bot.*trading", r"ai.*trade for me"],
                "answer": "Yes, the platform supports automated trading. Enable 'Auto-Trading Mode' on the AI Signals page, set your risk parameters (max position size, stop-loss percentage), and the AI will execute trades on your behalf when it identifies high-confidence opportunities. The system includes safeguards: 1-hour minimum hold, 4-hour cooldowns between repeat positions, and 75%+ confidence threshold for buys."
            },
            "backtest": {
                "patterns": [r"backtest", r"historical.*performance", r"past results"],
                "answer": "The Backtest Results page shows simulated performance of the AI strategy against a buy-and-hold benchmark over 1, 3, or 5-year periods. You can test on SPY, AAPL, NVDA, MSFT, TSLA, GOOGL, or QQQ. These are illustrative backtests — past performance does not guarantee future results."
            },
            "support": {
                "patterns": [r"help", r"support", r"contact", r"customer service"],
                "answer": "I'm here to help! Ask me anything about the platform, features, or trading. For technical issues or account-specific questions, please use the contact form in your Account page after registering."
            }
        }
    
    def _get_market_status(self) -> str:
        """Determine current market status"""
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()  # 0 = Monday, 6 = Sunday
        
        if weekday >= 5:  # Weekend
            return "closed (weekend — opens Monday 9:30 AM ET)"
        
        if hour < 6 or hour >= 20:  # Before 6 AM or after 8 PM PT
            return "closed (pre-market opens at 4:00 AM ET, regular hours 9:30 AM - 4:00 PM ET)"
        elif 6 <= hour < 9:  # 6-9 AM PT = pre-market
            return "in pre-market (regular hours 9:30 AM - 4:00 PM ET)"
        elif 13 <= hour < 17:  # 1-5 PM PT = regular hours
            return "open (9:30 AM - 4:00 PM ET)"
        else:
            return "closed (after-hours, regular hours 9:30 AM - 4:00 PM ET)"
    
    def get_response(self, user_message: str) -> str:
        """Get response for user message"""
        message_lower = user_message.lower().strip()
        
        # Check each knowledge category
        for category, data in self.knowledge.items():
            for pattern in data["patterns"]:
                if re.search(pattern, message_lower):
                    answer = data["answer"]
                    if "{market_status}" in answer:
                        answer = answer.replace("{market_status}", self._get_market_status())
                    return answer
        
        # Greeting
        if re.search(r"^(hi|hello|hey|greetings)", message_lower):
            return "Hello. I'm the Trade With AI assistant. Ask me about the platform, market hours, AI models, pricing, or anything else. What would you like to know?"
        
        # Thanks
        if re.search(r"^(thanks|thank you|thx|ty)", message_lower):
            return "You're welcome. Let me know if you have other questions."
        
        # Default fallback
        return "I can help with questions about: market hours, virtual cash, AI models, free trial, real-money trading, features, pricing, registration, auto-trading, backtests, and support. What would you like to know more about?"
    
    def get_suggested_questions(self) -> list:
        """Get list of suggested questions"""
        return [
            "When does the market open?",
            "How much virtual cash do I start with?",
            "How do the AI models work?",
            "Is this safe / is it a scam?",
            "What does it cost?",
            "How does auto-trading work?",
            "What can I do on the platform?",
            "Do I need to register?"
        ]


# Global instance
ai_assistant = AIAssistant()