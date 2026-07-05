"""
Stripe Payment Integration for TradeAI Signals
Handles subscriptions, one-time payments, and webhooks
"""
import stripe
import os
from datetime import datetime, timedelta
from config import PRICING


# Stripe API keys (set via environment variables for security)
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")

# Initialize Stripe
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# Price IDs (will be created in Stripe Dashboard)
PRICE_IDS = {
    "ai_weekly": os.environ.get("STRIPE_PRICE_AI_WEEKLY", "price_ai_weekly_placeholder"),
    "ai_monthly": os.environ.get("STRIPE_PRICE_AI_MONTHLY", "price_ai_monthly_placeholder"),
    "newsletter": os.environ.get("STRIPE_PRICE_NEWSLETTER", "price_newsletter_placeholder"),
    "real_money": os.environ.get("STRIPE_PRICE_REAL_MONEY", "price_real_money_placeholder"),
}


class StripeManager:
    """Manages Stripe payments and subscriptions"""
    
    def __init__(self):
        self.enabled = bool(STRIPE_SECRET_KEY)
    
    def create_customer(self, email: str, name: str) -> dict:
        """Create a Stripe customer"""
        if not self.enabled:
            return {"success": False, "error": "Stripe not configured"}
        
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={"source": "tradeai_signals"}
            )
            return {
                "success": True,
                "customer_id": customer.id,
                "email": customer.email
            }
        except stripe.error.StripeError as e:
            return {"success": False, "error": str(e)}
    
    def create_subscription(self, customer_id: str, plan: str) -> dict:
        """Create a subscription for a customer"""
        if not self.enabled:
            return {"success": False, "error": "Stripe not configured"}
        
        if plan not in PRICE_IDS:
            return {"success": False, "error": f"Unknown plan: {plan}"}
        
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": PRICE_IDS[plan]}],
                payment_behavior="default_incomplete",
                payment_settings={"save_default_payment_method": "on_subscription"},
                expand=["latest_invoice.payment_intent"],
            )
            
            return {
                "success": True,
                "subscription_id": subscription.id,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "status": subscription.status,
                "amount": subscription.latest_invoice.amount_due / 100
            }
        except stripe.error.StripeError as e:
            return {"success": False, "error": str(e)}
    
    def create_one_time_payment(self, customer_id: str, plan: str) -> dict:
        """Create a one-time payment (for real money onboarding)"""
        if not self.enabled:
            return {"success": False, "error": "Stripe not configured"}
        
        try:
            # Get the price for one-time payment
            price = stripe.Price.retrieve(PRICE_IDS[plan])
            
            intent = stripe.PaymentIntent.create(
                amount=price.unit_amount,
                currency="usd",
                customer=customer_id,
                metadata={"plan": plan},
                automatic_payment_methods={"enabled": True},
            )
            
            return {
                "success": True,
                "payment_intent_id": intent.id,
                "client_secret": intent.client_secret,
                "amount": intent.amount / 100
            }
        except stripe.error.StripeError as e:
            return {"success": False, "error": str(e)}
    
    def cancel_subscription(self, subscription_id: str) -> dict:
        """Cancel a subscription"""
        if not self.enabled:
            return {"success": False, "error": "Stripe not configured"}
        
        try:
            subscription = stripe.Subscription.delete(subscription_id)
            return {
                "success": True,
                "status": subscription.status,
                "canceled_at": subscription.canceled_at
            }
        except stripe.error.StripeError as e:
            return {"success": False, "error": str(e)}
    
    def get_subscription(self, subscription_id: str) -> dict:
        """Get subscription details"""
        if not self.enabled:
            return {"success": False, "error": "Stripe not configured"}
        
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                "success": True,
                "status": subscription.status,
                "current_period_end": subscription.current_period_end,
                "plan": subscription.items.data[0].price.id if subscription.items.data else None
            }
        except stripe.error.StripeError as e:
            return {"success": False, "error": str(e)}
    
    def create_checkout_session(self, plan: str, customer_email: str = None) -> dict:
        """Create a Stripe Checkout session (easier flow)"""
        if not self.enabled:
            return {"success": False, "error": "Stripe not configured"}
        
        try:
            price_id = PRICE_IDS.get(plan)
            if not price_id:
                return {"success": False, "error": f"Unknown plan: {plan}"}
            
            mode = "subscription" if plan != "real_money" else "payment"
            
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price": price_id,
                    "quantity": 1,
                }],
                mode=mode,
                success_url="https://tradeai-signals.streamlit.app/?success=true&session_id={CHECKOUT_SESSION_ID}",
                cancel_url="https://tradeai-signals.streamlit.app/?canceled=true",
                customer_email=customer_email,
                metadata={"plan": plan}
            )
            
            return {
                "success": True,
                "session_id": session.id,
                "url": session.url
            }
        except stripe.error.StripeError as e:
            return {"success": False, "error": str(e)}
    
    def handle_webhook(self, payload: str, sig_header: str) -> dict:
        """Handle Stripe webhook events"""
        if not self.enabled:
            return {"success": False, "error": "Stripe not configured"}
        
        webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
        
        try:
            if webhook_secret:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, webhook_secret
                )
            else:
                event = stripe.Event.construct_from(
                    stripe.util.json.loads(payload), stripe.api_key
                )
            
            # Handle different event types
            if event["type"] == "checkout.session.completed":
                session = event["data"]["object"]
                return {
                    "success": True,
                    "event": "checkout_completed",
                    "customer_id": session.get("customer"),
                    "subscription_id": session.get("subscription"),
                    "plan": session.get("metadata", {}).get("plan")
                }
            elif event["type"] == "customer.subscription.deleted":
                subscription = event["data"]["object"]
                return {
                    "success": True,
                    "event": "subscription_canceled",
                    "subscription_id": subscription["id"]
                }
            elif event["type"] == "invoice.payment_succeeded":
                invoice = event["data"]["object"]
                return {
                    "success": True,
                    "event": "payment_succeeded",
                    "customer_id": invoice.get("customer"),
                    "amount": invoice.get("amount_paid", 0) / 100
                }
            
            return {"success": True, "event": event["type"]}
        except (ValueError, stripe.error.SignatureVerificationError) as e:
            return {"success": False, "error": str(e)}


# Global instance
stripe_manager = StripeManager()


def get_plan_details(plan_id: str) -> dict:
    """Get details for a subscription plan"""
    plans = {
        "ai_weekly": {
            "name": "AI Signals (Weekly)",
            "price": PRICING.get("ai_signals_weekly", 9),
            "period": "week",
            "type": "subscription"
        },
        "ai_monthly": {
            "name": "AI Signals (Monthly)",
            "price": PRICING.get("ai_signals_monthly", 36),
            "period": "month",
            "type": "subscription"
        },
        "newsletter": {
            "name": "Investment Newsletter",
            "price": PRICING.get("newsletter_monthly", 19),
            "period": "month",
            "type": "subscription"
        },
        "real_money": {
            "name": "Real Money Onboarding",
            "price": PRICING.get("real_money_onboarding", 120),
            "period": "one-time",
            "type": "payment"
        }
    }
    return plans.get(plan_id, {})