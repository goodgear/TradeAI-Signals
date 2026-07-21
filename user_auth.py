"""
User Authentication and Subscription Management
"""
import json
import os
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Optional
from config import FREE_TRIAL_DAYS, PRICING
from alpaca_integration import encrypt_secret, decrypt_secret, quick_test


@dataclass
class User:
    """User account"""
    user_id: str
    name: str
    email: str
    password_hash: str
    created_at: str
    last_login: str
    subscription_type: str
    subscription_start: str
    trial_end: str
    is_active: bool = True
    # Alpaca brokerage (encrypted at rest; user connects their own account)
    alpaca_api_key_enc: Optional[str] = None
    alpaca_secret_key_enc: Optional[str] = None
    alpaca_paper: bool = True
    alpaca_account_id: Optional[str] = None
    alpaca_connected_at: Optional[str] = None
    alpaca_last_verified: Optional[str] = None


class UserAuth:
    """Handles user authentication and registration"""
    
    def __init__(self, data_dir: str = "users"):
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self.users: dict = {}
        
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        self._load_users()
    
    def _load_users(self):
        """Load users from file"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    data = json.load(f)
                    self.users = {u['user_id']: User(**u) for u in data}
            except:
                self.users = {}
    
    def _save_users(self):
        """Save users to file"""
        with open(self.users_file, 'w') as f:
            json.dump([asdict(u) for u in self.users.values()], f, indent=2)
    
    def _hash_password(self, password: str) -> str:
        """Simple password hashing"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_user_id(self) -> str:
        """Generate unique user ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def register(self, name: str, email: str, password: str) -> dict:
        """Register a new user with free trial"""
        for user in self.users.values():
            if user.email.lower() == email.lower():
                return {"success": False, "error": "Email already registered"}
        
        user_id = self._generate_user_id()
        now = datetime.now()
        trial_end = now + timedelta(days=FREE_TRIAL_DAYS)
        
        user = User(
            user_id=user_id,
            name=name,
            email=email,
            password_hash=self._hash_password(password),
            created_at=now.isoformat(),
            last_login=now.isoformat(),
            subscription_type='trial',
            subscription_start=now.isoformat(),
            trial_end=trial_end.isoformat()
        )
        
        self.users[user_id] = user
        self._save_users()
        
        return {
            "success": True,
            "user_id": user_id,
            "name": name,
            "email": email,
            "subscription_type": "trial",
            "trial_end": trial_end.isoformat(),
            "trial_days_remaining": FREE_TRIAL_DAYS
        }
    
    def login(self, email: str, password: str) -> dict:
        """Login user"""
        for user in self.users.values():
            if user.email.lower() == email.lower():
                if user.password_hash == self._hash_password(password):
                    user.last_login = datetime.now().isoformat()
                    self._save_users()
                    return {
                        "success": True,
                        "user_id": user.user_id,
                        "name": user.name,
                        "email": user.email,
                        "subscription_type": user.subscription_type,
                        "is_active": user.is_active
                    }
                else:
                    return {"success": False, "error": "Invalid password"}
        
        return {"success": False, "error": "Email not found"}
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def update_subscription(self, user_id: str, subscription_type: str) -> dict:
        """Update user subscription"""
        user = self.get_user(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        user.subscription_type = subscription_type
        user.subscription_start = datetime.now().isoformat()
        self._save_users()
        
        return {"success": True, "subscription_type": subscription_type}
    
    def check_trial_status(self, user_id: str) -> dict:
        """Check if trial is still active"""
        user = self.get_user(user_id)
        if not user:
            return {"active": False, "error": "User not found"}
        
        if user.subscription_type != 'trial':
            return {"active": True, "is_trial": False, "subscription_type": user.subscription_type}
        
        trial_end = datetime.fromisoformat(user.trial_end)
        now = datetime.now()
        
        if now > trial_end:
            return {"active": False, "is_trial": True, "days_remaining": 0}
        
        return {"active": True, "is_trial": True, "days_remaining": (trial_end - now).days}

    # ----- ALPACA BROKERAGE CONNECTION -----

    def connect_alpaca(self, user_id: str, api_key: str, secret_key: str,
                       paper: bool = True) -> dict:
        """
        Validate and store user's Alpaca credentials.
        Tests connection first — never stores keys that don't work.
        """
        user = self.get_user(user_id)
        if not user:
            return {"success": False, "error": "User not found"}

        # Test the credentials BEFORE saving anything
        test = quick_test(api_key, secret_key, paper=paper)
        if not test["success"]:
            return {"success": False, "error": f"Connection failed: {test.get('error', 'unknown')}"}

        # Encrypt and store
        try:
            user.alpaca_api_key_enc = encrypt_secret(api_key)
            user.alpaca_secret_key_enc = encrypt_secret(secret_key)
            user.alpaca_paper = paper
            user.alpaca_account_id = test.get("account_id")
            user.alpaca_connected_at = datetime.now().isoformat()
            user.alpaca_last_verified = datetime.now().isoformat()
            self._save_users()

            return {
                "success": True,
                "account_id": user.alpaca_account_id,
                "is_paper": paper,
                "equity": test.get("equity"),
                "buying_power": test.get("buying_power"),
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to save credentials: {e}"}

    def disconnect_alpaca(self, user_id: str) -> dict:
        """Remove user's stored Alpaca credentials. Their broker account is unaffected."""
        user = self.get_user(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        if not user.alpaca_api_key_enc:
            return {"success": False, "error": "No Alpaca account connected"}

        user.alpaca_api_key_enc = None
        user.alpaca_secret_key_enc = None
        user.alpaca_paper = True
        user.alpaca_account_id = None
        user.alpaca_connected_at = None
        user.alpaca_last_verified = None
        self._save_users()
        return {"success": True}

    def get_alpaca_client(self, user_id: str):
        """
        Return a live AlpacaClient for the user, or None if not connected.
        Caller is responsible for NOT logging the client or its keys.
        """
        from alpaca_integration import AlpacaClient  # late import for speed
        user = self.get_user(user_id)
        if not user or not user.alpaca_api_key_enc:
            return None
        try:
            api_key = decrypt_secret(user.alpaca_api_key_enc)
            secret_key = decrypt_secret(user.alpaca_secret_key_enc)
            return AlpacaClient(api_key, secret_key, paper=user.alpaca_paper)
        except Exception as e:
            return None

    def is_alpaca_connected(self, user_id: str) -> bool:
        user = self.get_user(user_id)
        return bool(user and user.alpaca_api_key_enc)


class SubscriptionManager:
    """Manages subscriptions and billing"""
    
    def __init__(self):
        self.pricing = PRICING
    
    def get_available_plans(self) -> list:
        """Get available subscription plans"""
        return [
            {
                "id": "ai_weekly",
                "name": "AI Trading Signals",
                "price": self.pricing['ai_signals_weekly'],
                "period": "week",
                "features": ["Real-time AI buy/sell signals", "Automatic ticker recommendations", "Portfolio tracking", "Technical analysis dashboard"]
            },
            {
                "id": "ai_monthly",
                "name": "AI Trading Signals",
                "price": self.pricing['ai_signals_monthly'],
                "period": "month",
                "features": ["Everything in Weekly", "Save 10% vs weekly", "Priority support", "Advanced AI models"]
            },
            {
                "id": "newsletter",
                "name": "Investment Newsletter",
                "price": self.pricing['newsletter_monthly'],
                "period": "month",
                "features": ["Weekly market insights", "Educational content", "Stock picks & analysis", "Market trend reports"]
            },
            {
                "id": "real_money",
                "name": "Real Money Trading",
                "price": self.pricing['real_money_onboarding'],
                "period": "one-time",
                "features": ["SEC-compliant setup", "Broker integration", "10% bi-weekly fee on gains", "Priority support 24/7"]
            }
        ]
    
    def calculate_gains_fee(self, gains: float) -> float:
        """Calculate bi-weekly gains fee"""
        return gains * (self.pricing['gains_percentage'] / 100)


# Global instances
user_auth = UserAuth()
subscription_manager = SubscriptionManager()
