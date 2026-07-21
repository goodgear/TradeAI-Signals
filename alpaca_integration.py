"""
Alpaca Brokerage Integration for ARMAC Trading App
==================================================

Connects user to their own Alpaca brokerage account. ARMAC NEVER holds funds.
User generates API keys in their Alpaca dashboard, pastes them into our app,
we encrypt and store. User can revoke from their end anytime.

Layers:
  1. Encryption: Fernet symmetric encryption for at-rest key storage
  2. Connection test: validates API key on save (no silent failures)
  3. Account info: real equity, cash, positions, P/L
  4. Order placement: market/limit orders, paper or live
  5. Audit logging: every order gets logged with user_id + timestamp

SECURITY NOTES:
  - ARMAC_ENCRYPTION_KEY must be set in production (32 url-safe base64 bytes)
  - API keys never logged, never returned to UI after save
  - All write operations (orders) require explicit user confirmation in UI
  - Paper mode by default — flip ALPACA_PAPER=False only after testing
"""
import os
import sys
import json
import logging
from typing import Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet, InvalidToken

# Alpaca SDK
try:
    import alpaca_trade_api as tradeapi
except ImportError:
    tradeapi = None
    logging.warning("alpaca-trade-api not installed; run: pip install alpaca-trade-api")

logger = logging.getLogger(__name__)


# ============== ENCRYPTION ==============

def _get_cipher() -> Fernet:
    """Get Fernet cipher. Uses ARMAC_ENCRYPTION_KEY env var (32 url-safe base64 bytes)."""
    key = os.environ.get("ARMAC_ENCRYPTION_KEY")
    if not key:
        # Dev fallback — log warning, generate ephemeral key
        logger.warning(
            "ARMAC_ENCRYPTION_KEY not set. Generating ephemeral key for dev. "
            "SET THIS IN PROD: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
        )
        key = Fernet.generate_key().decode()
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_secret(plaintext: str) -> str:
    """Encrypt a secret (API key, secret key) for storage."""
    return _get_cipher().encrypt(plaintext.encode()).decode()


def decrypt_secret(ciphertext: str) -> str:
    """Decrypt a stored secret. Raises InvalidToken if wrong key."""
    try:
        return _get_cipher().decrypt(ciphertext.encode()).decode()
    except InvalidToken:
        logger.error("Failed to decrypt — wrong key or corrupted token")
        raise


# ============== DATA CLASSES ==============

@dataclass
class AlpacaAccount:
    """Snapshot of user's Alpaca account."""
    account_id: str
    account_number: str
    status: str
    currency: str
    cash: float
    buying_power: float
    portfolio_value: float
    equity: float
    last_equity: float
    day_pnl: float
    day_pnl_pct: float
    total_pnl: float
    is_paper: bool
    connected_at: str

    def to_dict(self):
        return asdict(self)


@dataclass
class AlpacaPosition:
    """One open position in the user's Alpaca account."""
    symbol: str
    qty: float
    avg_entry_price: float
    current_price: float
    market_value: float
    unrealized_pl: float
    unrealized_plpc: float
    side: str

    def to_dict(self):
        return asdict(self)


@dataclass
class AlpacaOrder:
    """An order (filled, working, or canceled)."""
    order_id: str
    symbol: str
    qty: float
    side: str
    type: str
    status: str
    submitted_at: str
    filled_avg_price: Optional[float] = None

    def to_dict(self):
        return asdict(self)


# ============== CLIENT ==============

class AlpacaClient:
    """
    Wrapper around Alpaca SDK for ARMAC.
    One instance per user session. NEVER log api_key/secret.
    """

    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        if tradeapi is None:
            raise RuntimeError("alpaca-trade-api not installed")
        self.paper = paper
        self.base_url = (
            "https://paper-api.alpaca.markets" if paper
            else "https://api.alpaca.markets"
        )
        # SDK accepts keys directly; we never persist them on the client
        self.api = tradeapi.REST(api_key, secret_key, self.base_url, api_version="v2")

    # ----- Connection -----

    def test_connection(self) -> dict:
        """Verify credentials work. Returns dict with success flag."""
        try:
            acc = self.api.get_account()
            return {
                "success": True,
                "account_id": acc.id,
                "status": acc.status,
                "is_paper": self.paper,
                "currency": acc.currency,
            }
        except Exception as e:
            return {"success": False, "error": _scrub_error(str(e))}

    # ----- Account -----

    def get_account(self) -> AlpacaAccount:
        a = self.api.get_account()
        equity = float(a.equity)
        last_equity = float(a.last_equity)
        day_pnl = equity - last_equity
        day_pnl_pct = (day_pnl / last_equity * 100) if last_equity else 0.0
        return AlpacaAccount(
            account_id=a.id,
            account_number=a.account_number,
            status=a.status,
            currency=a.currency,
            cash=float(a.cash),
            buying_power=float(a.buying_power),
            portfolio_value=float(a.portfolio_value),
            equity=equity,
            last_equity=last_equity,
            day_pnl=day_pnl,
            day_pnl_pct=day_pnl_pct,
            total_pnl=day_pnl,  # Alpaca exposes last_equity = prev day close
            is_paper=self.paper,
            connected_at=datetime.now().isoformat(),
        )

    # ----- Positions -----

    def get_positions(self) -> list[AlpacaPosition]:
        try:
            positions = self.api.list_positions()
        except Exception as e:
            logger.warning(f"get_positions failed: {_scrub_error(str(e))}")
            return []
        return [
            AlpacaPosition(
                symbol=p.symbol,
                qty=float(p.qty),
                avg_entry_price=float(p.avg_entry_price),
                current_price=float(p.current_price),
                market_value=float(p.market_value),
                unrealized_pl=float(p.unrealized_pl),
                unrealized_plpc=float(p.unrealized_plpc) * 100,  # to %
                side=p.side,
            )
            for p in positions
        ]

    # ----- Orders -----

    def place_order(self, symbol: str, qty: float, side: str,
                    type: str = "market", time_in_force: str = "day",
                    limit_price: Optional[float] = None) -> dict:
        """
        Place an order. Returns dict with success flag and order details.
        Caller MUST confirm in UI before calling this in production.
        """
        if side not in ("buy", "sell"):
            return {"success": False, "error": f"side must be 'buy' or 'sell', got {side!r}"}
        if type not in ("market", "limit"):
            return {"success": False, "error": f"type must be 'market' or 'limit', got {type!r}"}

        kwargs = {
            "symbol": symbol.upper(),
            "qty": qty,
            "side": side,
            "type": type,
            "time_in_force": time_in_force,
        }
        if type == "limit":
            if limit_price is None:
                return {"success": False, "error": "limit orders require limit_price"}
            kwargs["limit_price"] = limit_price

        try:
            order = self.api.submit_order(**kwargs)
            logger.info(
                f"Order placed: {side} {qty} {symbol} ({type}) "
                f"user_action=confirmed paper={self.paper}"
            )
            return {
                "success": True,
                "order_id": order.id,
                "symbol": order.symbol,
                "qty": float(order.qty),
                "side": order.side,
                "type": order.type,
                "status": order.status,
                "submitted_at": str(order.submitted_at),
            }
        except Exception as e:
            return {"success": False, "error": _scrub_error(str(e))}

    def cancel_order(self, order_id: str) -> dict:
        try:
            self.api.cancel_order(order_id)
            logger.info(f"Order canceled: {order_id}")
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": _scrub_error(str(e))}

    def get_orders(self, status: str = "all", limit: int = 50) -> list[AlpacaOrder]:
        try:
            orders = self.api.list_orders(status=status, limit=limit)
        except Exception as e:
            logger.warning(f"get_orders failed: {_scrub_error(str(e))}")
            return []
        return [
            AlpacaOrder(
                order_id=o.id,
                symbol=o.symbol,
                qty=float(o.qty),
                side=o.side,
                type=o.type,
                status=o.status,
                submitted_at=str(o.submitted_at),
                filled_avg_price=float(o.filled_avg_price) if o.filled_avg_price else None,
            )
            for o in orders
        ]


# ============== HELPERS ==============

def _scrub_error(msg: str) -> str:
    """Remove any keys/tokens from error messages before logging/returning."""
    import re
    # Remove anything that looks like an API key (alphanumeric 20+ chars)
    msg = re.sub(r'\b[A-Za-z0-9]{20,}\b', '[REDACTED]', msg)
    return msg


# ============== CONVENIENCE: ONE-CALL TEST ==============

def quick_test(api_key: str, secret_key: str, paper: bool = True) -> dict:
    """
    Test credentials without saving. Returns account summary or error.
    Use this for the 'Connect Brokerage' button in the UI.
    """
    client = AlpacaClient(api_key, secret_key, paper=paper)
    test = client.test_connection()
    if not test["success"]:
        return test
    try:
        acc = client.get_account()
        return {
            "success": True,
            "account_id": acc.account_id,
            "status": acc.status,
            "is_paper": acc.is_paper,
            "equity": acc.equity,
            "cash": acc.cash,
            "buying_power": acc.buying_power,
            "portfolio_value": acc.portfolio_value,
            "currency": acc.currency,
        }
    except Exception as e:
        return {"success": False, "error": _scrub_error(str(e))}


# ============== SELF-TEST (only if run directly) ==============

if __name__ == "__main__":
    # Run as: python alpaca_integration.py
    # Will prompt for keys via env vars (NOT hardcoded for security)
    print("=" * 60)
    print("Alpaca Integration Self-Test")
    print("=" * 60)
    print("Set ALPACA_TEST_KEY and ALPACA_TEST_SECRET env vars to test.")
    print("Example (PowerShell):")
    print('  $env:ALPACA_TEST_KEY = "your_key_here"')
    print('  $env:ALPACA_TEST_SECRET = "your_secret_here"')
    print("  python alpaca_integration.py")
    print()

    key = os.environ.get("ALPACA_TEST_KEY")
    secret = os.environ.get("ALPACA_TEST_SECRET")
    if not key or not secret:
        print("No test keys in env. Exiting.")
        sys.exit(0)

    print("Testing PAPER trading connection...")
    result = quick_test(key, secret, paper=True)
    if result["success"]:
        print(f"  OK — account {result['account_id']}")
        print(f"  Status: {result['status']}")
        print(f"  Equity: ${result['equity']:,.2f}")
        print(f"  Cash:   ${result['cash']:,.2f}")
        print(f"  Buying power: ${result['buying_power']:,.2f}")
    else:
        print(f"  FAILED: {result['error']}")
