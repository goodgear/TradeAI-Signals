"""
Portfolio Manager - Handles simulated trading and portfolio tracking
"""
import json
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Optional
from config import INITIAL_BALANCE


@dataclass
class Position:
    """Represents a stock position"""
    ticker: str
    shares: float
    entry_price: float
    entry_date: str
    current_price: float = 0
    
    @property
    def market_value(self) -> float:
        return self.shares * self.current_price
    
    @property
    def cost_basis(self) -> float:
        return self.shares * self.entry_price
    
    @property
    def unrealized_pnl(self) -> float:
        return self.market_value - self.cost_basis
    
    @property
    def unrealized_pnl_pct(self) -> float:
        if self.cost_basis == 0:
            return 0
        return (self.unrealized_pnl / self.cost_basis) * 100


@dataclass
class Trade:
    """Records a trade execution"""
    timestamp: str
    action: str  # BUY or SELL
    ticker: str
    shares: float
    price: float
    total: float
    pnl: float = 0  # For SELL trades


class Portfolio:
    """Manages simulated portfolio and trades"""
    
    def __init__(self, initial_balance: float = INITIAL_BALANCE, user_id: str = "default"):
        self.initial_balance = initial_balance
        self.cash = initial_balance
        self.positions: List[Position] = []
        self.trade_history: List[Trade] = []
        self.user_id = user_id
        self.creation_date = datetime.now().isoformat()
        self.last_updated = self.creation_date
    
    @property
    def total_value(self) -> float:
        """Total portfolio value (cash + positions)"""
        positions_value = sum(p.market_value for p in self.positions)
        return self.cash + positions_value
    
    @property
    def total_pnl(self) -> float:
        """Total profit/loss"""
        return self.total_value - self.initial_balance
    
    @property
    def total_pnl_pct(self) -> float:
        """Total return percentage"""
        if self.initial_balance == 0:
            return 0
        return (self.total_pnl / self.initial_balance) * 100
    
    def get_position(self, ticker: str) -> Optional[Position]:
        """Get position for a ticker"""
        for pos in self.positions:
            if pos.ticker == ticker.upper():
                return pos
        return None
    
    def can_buy(self, ticker: str, shares: float, price: float) -> bool:
        """Check if buy is possible"""
        total_cost = shares * price * 1.001  # ~0.1% fee
        return self.cash >= total_cost
    
    def execute_buy(self, ticker: str, shares: float, price: float) -> dict:
        """
        Execute a BUY order
        
        Returns:
            Dict with result and updated portfolio state
        """
        ticker = ticker.upper()
        total_cost = shares * price * 1.001  # ~0.1% fee
        
        if self.cash < total_cost:
            return {
                "success": False,
                "error": f"Insufficient funds. Need ${total_cost:.2f}, have ${self.cash:.2f}"
            }
        
        # Check if we already have a position
        existing = self.get_position(ticker)
        
        if existing:
            # Average in
            total_shares = existing.shares + shares
            total_cost_basis = existing.cost_basis + (shares * price)
            new_avg_price = total_cost_basis / total_shares
            
            existing.shares = total_shares
            existing.entry_price = new_avg_price
        else:
            # New position
            position = Position(
                ticker=ticker,
                shares=shares,
                entry_price=price,
                entry_date=datetime.now().isoformat(),
                current_price=price
            )
            self.positions.append(position)
        
        self.cash -= total_cost
        
        trade = Trade(
            timestamp=datetime.now().isoformat(),
            action="BUY",
            ticker=ticker,
            shares=shares,
            price=price,
            total=total_cost
        )
        self.trade_history.append(trade)
        self.last_updated = datetime.now().isoformat()
        
        return {
            "success": True,
            "action": "BUY",
            "ticker": ticker,
            "shares": shares,
            "price": price,
            "total": total_cost,
            "cash_remaining": self.cash
        }
    
    def execute_sell(self, ticker: str, shares: float, price: float) -> dict:
        """
        Execute a SELL order
        
        Returns:
            Dict with result and updated portfolio state
        """
        ticker = ticker.upper()
        position = self.get_position(ticker)
        
        if not position:
            return {
                "success": False,
                "error": f"No position in {ticker}"
            }
        
        if shares > position.shares:
            shares = position.shares  # Sell what we have
        
        total_proceeds = shares * price * 0.999  # ~0.1% fee
        pnl = (price - position.entry_price) * shares
        
        if shares >= position.shares:
            # Close entire position
            self.positions = [p for p in self.positions if p.ticker != ticker]
        else:
            position.shares -= shares
        
        self.cash += total_proceeds
        
        trade = Trade(
            timestamp=datetime.now().isoformat(),
            action="SELL",
            ticker=ticker,
            shares=shares,
            price=price,
            total=total_proceeds,
            pnl=pnl
        )
        self.trade_history.append(trade)
        self.last_updated = datetime.now().isoformat()
        
        return {
            "success": True,
            "action": "SELL",
            "ticker": ticker,
            "shares": shares,
            "price": price,
            "proceeds": total_proceeds,
            "pnl": pnl,
            "cash_remaining": self.cash
        }
    
    def update_prices(self, prices: dict):
        """Update current prices for all positions"""
        for position in self.positions:
            if position.ticker in prices:
                position.current_price = prices[position.ticker]
        self.last_updated = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """Convert portfolio to dictionary"""
        return {
            "initial_balance": self.initial_balance,
            "cash": self.cash,
            "total_value": self.total_value,
            "total_pnl": self.total_pnl,
            "total_pnl_pct": self.total_pnl_pct,
            "positions": [asdict(p) for p in self.positions],
            "trade_history": [asdict(t) for t in self.trade_history],
            "creation_date": self.creation_date,
            "last_updated": self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Portfolio':
        """Create portfolio from dictionary"""
        portfolio = cls(
            initial_balance=data.get("initial_balance", INITIAL_BALANCE),
            user_id=data.get("user_id", "default")
        )
        portfolio.cash = data.get("cash", portfolio.initial_balance)
        portfolio.creation_date = data.get("creation_date", datetime.now().isoformat())
        portfolio.last_updated = data.get("last_updated", datetime.now().isoformat())
        
        # Restore positions
        for pos_data in data.get("positions", []):
            position = Position(**pos_data)
            portfolio.positions.append(position)
        
        # Restore trade history
        for trade_data in data.get("trade_history", []):
            trade = Trade(**trade_data)
            portfolio.trade_history.append(trade)
        
        return portfolio
    
    def save(self, filepath: str = None):
        """Save portfolio to file"""
        if filepath is None:
            filepath = f"portfolio_{self.user_id}.json"
        
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> 'Portfolio':
        """Load portfolio from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


# Portfolio Manager - handles multiple portfolios
class PortfolioManager:
    """Manages multiple user portfolios"""
    
    def __init__(self, data_dir: str = "portfolios"):
        self.data_dir = data_dir
        self.portfolios: dict = {}
        
        # Create data directory if needed
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def get_portfolio(self, user_id: str) -> Portfolio:
        """Get or create portfolio for user"""
        if user_id not in self.portfolios:
            filepath = os.path.join(self.data_dir, f"{user_id}.json")
            if os.path.exists(filepath):
                self.portfolios[user_id] = Portfolio.load(filepath)
            else:
                self.portfolios[user_id] = Portfolio(user_id=user_id)
        
        return self.portfolios[user_id]
    
    def save_portfolio(self, user_id: str):
        """Save portfolio to disk"""
        if user_id in self.portfolios:
            filepath = os.path.join(self.data_dir, f"{user_id}.json")
            self.portfolios[user_id].save(filepath)
    
    def delete_portfolio(self, user_id: str):
        """Delete user portfolio"""
        filepath = os.path.join(self.data_dir, f"{user_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
        if user_id in self.portfolios:
            del self.portfolios[user_id]


# Global instance
portfolio_manager = PortfolioManager()
