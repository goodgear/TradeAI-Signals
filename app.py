"""
AI Trading Signal App - Main Streamlit Application
High-tech interface for AI-powered stock trading with fake money
"""
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import random

# Import our modules
from trading_engine import trading_engine
from prediction_model import predictor
from portfolio_manager import portfolio_manager, Portfolio
from user_auth import user_auth, subscription_manager
from stripe_integration import stripe_manager, get_plan_details
from config import THEME, INITIAL_BALANCE, DEFAULT_TICKERS, PRICING

# Page configuration
st.set_page_config(
    page_title="Trade With AI - Virtual Stock Trading",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# SVG Icons - High-Tech Neon Theme
ICONS = {
    "dashboard": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#00D4FF" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/></svg>''',
    "search": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#00D4FF" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>''',
    "portfolio": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#00D4FF" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>''',
    "ai": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#00D4FF" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 1v6m0 10v6m11-11h-6m-10 0H1m17.07-7.07l-4.24 4.24m-5.66 5.66l-4.24 4.24m0-14.14l4.24 4.24m5.66 5.66l4.24 4.24"/></svg>''',
    "trade": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#00D4FF" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>''',
    "subscribe": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#00D4FF" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>''',
    "account": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#00D4FF" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>''',
    "chart": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#00D4FF" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>''',
    "money": '''<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#00FF88" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>''',
    "user": '''<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#00D4FF" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>''',
    "buy": '''<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#00FF88" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>''',
    "sell": '''<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FF4757" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>''',
    "logo": '''<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" fill="none"><circle cx="16" cy="16" r="14" stroke="#00D4FF" stroke-width="1.5"/><path d="M10 20 L16 8 L22 20 M12.5 16 L19.5 16" stroke="#00D4FF" stroke-width="1.5" fill="none" stroke-linecap="round"/><circle cx="16" cy="16" r="2" fill="#00D4FF"/></svg>''',
}

# Custom CSS for high-tech neon theme
st.markdown("""
<style>
    /* Import tech font */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500&family=Rajdhani:wght@400;500;600&display=swap');
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0A0E17 0%, #1A1F2E 100%);
    }
    
    /* Headers - High Tech Neon Style */
    h1, h2, h3, h4 {
        color: #00D4FF !important;
        font-weight: 400 !important;
        font-family: 'Orbitron', 'Rajdhani', sans-serif !important;
        text-shadow: 0 0 5px #00D4FF, 0 0 10px #00D4FF, 0 0 20px #00D4FF !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
    }
    
    /* Subheaders */
    .stMarkdown h3, .stMarkdown h4 {
        color: #00D4FF !important;
        font-weight: 400 !important;
        font-family: 'Rajdhani', sans-serif !important;
        text-shadow: 0 0 5px rgba(0, 212, 255, 0.8), 0 0 10px rgba(0, 212, 255, 0.4) !important;
        letter-spacing: 1px !important;
    }
    
    /* Sidebar headers */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #00D4FF !important;
        font-weight: 400 !important;
        font-family: 'Orbitron', sans-serif !important;
        text-shadow: 0 0 8px #00D4FF, 0 0 15px rgba(0, 212, 255, 0.5) !important;
    }
    
    /* Neon glow filter for SVG icons */
    .neon-icon {
        filter: drop-shadow(0 0 3px #00D4FF) drop-shadow(0 0 6px #00D4FF);
        transition: all 0.3s ease;
    }
    
    .neon-icon:hover {
        filter: drop-shadow(0 0 5px #00D4FF) drop-shadow(0 0 10px #00D4FF);
    }
    
    /* Radio buttons in sidebar - tech style */
    .stRadio > label {
        background: transparent !important;
    }
    
    .stRadio [role="radiogroup"] label {
        background: rgba(26, 31, 46, 0.5) !important;
        border: 1px solid rgba(0, 212, 255, 0.2) !important;
        border-radius: 8px !important;
        padding: 10px !important;
        margin: 4px 0 !important;
        transition: all 0.3s ease !important;
    }
    
    .stRadio [role="radiogroup"] label:hover {
        border-color: #00D4FF !important;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.3) !important;
    }
    
    /* Cards */
    .css-1r6slb0 {
        background: #1A1F2E !important;
        border: 1px solid #2D3748 !important;
        border-radius: 12px !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00D4FF, #7B2FFF);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00B8E6, #6B1FDF);
    }
    
    /* Buy/Sell buttons */
    .buy-button {
        background: #00FF88 !important;
        color: #000 !important;
    }
    
    .sell-button {
        background: #FF4757 !important;
        color: #FFF !important;
    }
    
    /* Metrics */
    .metric-card {
        background: #1A1F2E;
        border: 1px solid #2D3748;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
    
    /* Price green/red */
    .price-up { color: #00FF88; }
    .price-down { color: #FF4757; }
    
    /* Signal badges */
    .signal-buy {
        background: #00FF88;
        color: #000;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
    }
    
    .signal-sell {
        background: #FF4757;
        color: #FFF;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
    }
    
    .signal-hold {
        background: #FFD93D;
        color: #000;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: #0D1117;
    }
    
    /* Dataframe */
    .dataframe {
        background: #1A1F2E !important;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #00D4FF, #00FF88);
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    """Initialize Streamlit session state variables"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'subscription_type' not in st.session_state:
        st.session_state.subscription_type = 'trial'
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = Portfolio(user_id="guest")
    if 'selected_ticker' not in st.session_state:
        st.session_state.selected_ticker = "AAPL"
    if 'auto_trade' not in st.session_state:
        st.session_state.auto_trade = False


init_session_state()


def has_ai_access() -> bool:
    """Check if user has access to AI signals"""
    if st.session_state.user_id is None:
        return True  # Guest/demo mode has access
    
    if st.session_state.subscription_type == 'trial':
        # Check if trial is still active
        status = user_auth.check_trial_status(st.session_state.user_id)
        return status.get('active', False)
    
    # Paid subscriptions have access
    return st.session_state.subscription_type in ['ai_weekly', 'ai_monthly', 'real_money']


def show_access_required():
    """Show subscription required message"""
    st.warning("🔒 **AI Signals Locked**")
    st.markdown("""
    Upgrade to unlock AI trading signals!
    
    | Plan | Price | Access |
    |------|-------|--------|
    | AI Signals (Weekly) | $9/week | Full AI Access |
    | AI Signals (Monthly) | $36/month | Full AI Access |
    | Real Money Mode | $120 + 10% gains | Full AI + Trading |
    
    **[Subscribe Now](http://localhost:8501/?page=Subscribe)** to continue!
    """)
    st.stop()


def show_trial_ending_warning():
    """Show warning if trial is ending soon"""
    if st.session_state.user_id and st.session_state.subscription_type == 'trial':
        status = user_auth.check_trial_status(st.session_state.user_id)
        if status.get('active') and status.get('days_remaining', 0) <= 1:
            st.warning(f"⚠️ **Trial ending soon!** {status.get('days_remaining')} day(s) remaining. Subscribe to keep AI access!")


# ==================== SIDEBAR ====================
def render_sidebar():
    """Render sidebar with navigation and user info"""
    with st.sidebar:
        # Logo with SVG
        col_logo, col_title = st.columns([1, 4])
        with col_logo:
            st.markdown(f'<div class="neon-icon">{ICONS["logo"]}</div>', unsafe_allow_html=True)
        with col_title:
            st.markdown("## TRADE WITH AI")
        
        # User status
        if st.session_state.user_id:
            st.success(f"👤 {st.session_state.user_name}")
            
            # Trial status
            if st.session_state.subscription_type == 'trial':
                status = user_auth.check_trial_status(st.session_state.user_id)
                if status.get('active'):
                    st.info(f"⏰ Trial: {status.get('days_remaining', 0)} days left")
                else:
                    st.warning("Trial expired")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.user_id = None
                st.session_state.user_name = None
                st.rerun()
        else:
            st.info("👤 Guest Mode")
        
        st.divider()
        
        # Navigation
        st.markdown("### NAVIGATION")
        page = st.radio(
            "Go to",
            ["Dashboard", "Search", "Portfolio", "AI Signals", 
             "Trade", "Subscribe", "Account"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Portfolio summary
        portfolio = st.session_state.portfolio
        st.markdown("### 💰 Portfolio")
        st.metric("Balance", f"${portfolio.cash:,.2f}")
        st.metric("Total Value", f"${portfolio.total_value:,.2f}")
        pnl_color = "#00FF88" if portfolio.total_pnl >= 0 else "#FF4757"
        st.markdown(f"<p style='color:{pnl_color}'>P/L: ${portfolio.total_pnl:,.2f} ({portfolio.total_pnl_pct:+.2f}%)</p>", unsafe_allow_html=True)
        
        return page


# ==================== LANDING PAGE ====================
def render_landing_page():
    """Beautiful landing page - first impression"""
    
    # Hero section
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px;">
        <h1 style="font-size: 56px; margin-bottom: 10px;">TRADE WITH AI</h1>
        <p style="color: #00D4FF; font-size: 20px; letter-spacing: 3px; margin-bottom: 30px;">
            EXPERIENCE THE FUTURE OF INVESTING
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Hook
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(0,212,255,0.1), rgba(123,47,255,0.1)); 
                    padding: 30px; border-radius: 16px; text-align: center; 
                    border: 1px solid rgba(0,212,255,0.3); margin-bottom: 30px;">
            <h2 style="color: #00D4FF; font-size: 24px; margin: 0 0 15px 0;">
                START WITH $10,000 VIRTUAL CASH
            </h2>
            <p style="color: #E8E8E8; font-size: 16px; margin: 10px 0;">
                No credit card. No risk. No experience needed.
            </p>
            <p style="color: #00FF88; font-size: 14px; margin: 10px 0;">
                ✓ Try instantly · ✓ Real market data · ✓ AI-guided trades
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # CTA - Start trading button
        if st.button("START TRADING NOW", use_container_width=True, type="primary"):
            # Set anonymous guest mode for first 3 days
            if 'anonymous_start_date' not in st.session_state:
                st.session_state.anonymous_start_date = datetime.now()
                st.session_state.anonymous_id = f"guest_{random.randint(1000, 9999)}"
                st.session_state.portfolio = Portfolio(user_id=st.session_state.anonymous_id)
            st.session_state.show_landing = False
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Main description
    st.markdown("""
    <div style="max-width: 900px; margin: 0 auto; padding: 20px;">
        <h3 style="text-align: center; color: #00D4FF;">WHY TRADE WITH AI?</h3>
        <p style="color: #E8E8E8; font-size: 16px; line-height: 1.8; text-align: center;">
            Whether you're taking your first steps into the market or you've been watching from the sidelines, 
            <b style="color: #00D4FF;">Trade With AI</b> offers something rare: a place to learn, experiment, 
            and gain genuine confidence using <b>virtual cash</b> in a real market environment — completely risk-free.
        </p>
        <p style="color: #E8E8E8; font-size: 16px; line-height: 1.8; text-align: center;">
            Our advanced artificial intelligence analyzes markets in real-time, identifies opportunities, 
            and guides your decisions. You stay in control while the heavy lifting happens in the background.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Features grid
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: #1A1F2E; padding: 25px; border-radius: 12px; 
                    border: 1px solid rgba(0,212,255,0.2); height: 250px;">
            <h4 style="color: #00D4FF;">🎓 LEARN BY DOING</h4>
            <p style="color: #E8E8E8; font-size: 14px;">
                Experience real market dynamics without risking a single dollar. 
                Virtual cash lets you make mistakes, learn patterns, and build intuition.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #1A1F2E; padding: 25px; border-radius: 12px; 
                    border: 1px solid rgba(0,212,255,0.2); height: 250px;">
            <h4 style="color: #00D4FF;">🤖 AI-POWERED INSIGHTS</h4>
            <p style="color: #E8E8E8; font-size: 14px;">
                Our ensemble of machine learning models — Random Forest, Gradient Boosting, 
                and Logistic Regression — work together to surface high-probability opportunities.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: #1A1F2E; padding: 25px; border-radius: 12px; 
                    border: 1px solid rgba(0,212,255,0.2); height: 250px;">
            <h4 style="color: #00D4FF;">⚡ ZERO FRICTION</h4>
            <p style="color: #E8E8E8; font-size: 14px;">
                Start in seconds. No lengthy signups, no overwhelming charts, 
                no financial jargon. Just clear signals and smart defaults.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Tech section - smaller font, for the curious
    with st.expander("🔬 For the curious — what's under the hood?"):
        st.markdown("""
        <div style="background: #1A1F2E; padding: 20px; border-radius: 12px; 
                    border: 1px solid rgba(0,212,255,0.2); font-size: 13px; line-height: 1.7;">
            <p style="color: #00D4FF;"><b>AI PREDICTION ENGINE</b></p>
            <ul style="color: #E8E8E8;">
                <li><b>Random Forest Classifier</b> — Pattern recognition across 17+ market features</li>
                <li><b>Gradient Boosting</b> — Sequential learning from past market behavior</li>
                <li><b>Logistic Regression</b> — Probability baseline for confidence calibration</li>
                <li><b>Ensemble Voter</b> — Consensus mechanism that weighs all models</li>
                <li><b>Technical Analysis Layer</b> — RSI, MACD, Bollinger Bands, Stochastic, OBV</li>
            </ul>
            
            <p style="color: #00D4FF;"><b>DATA & EXECUTION</b></p>
            <ul style="color: #E8E8E8;">
                <li><b>Real-time market data</b> via Yahoo Finance API</li>
                <li><b>Interactive charts</b> powered by Plotly</li>
                <li><b>SEC-compliant onboarding</b> for real-money transition</li>
                <li><b>Automated buying & selling</b> with smart stop-loss protection</li>
            </ul>
            
            <p style="color: #00D4FF;"><b>BUILT FOR BEGINNERS</b></p>
            <p style="color: #E8E8E8;">
                You don't need to know anything about investing. The AI handles analysis, 
                surfaces opportunities, and can execute trades on your behalf. 
                You focus on learning; we handle the complexity.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Pricing reminder
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background: #1A1F2E; padding: 25px; border-radius: 12px; 
                    border: 1px solid rgba(255,217,61,0.3); text-align: center;">
            <h4 style="color: #FFD93D;">YOUR FIRST 3 DAYS ARE FREE</h4>
            <p style="color: #E8E8E8;">
                On day 3, we'll invite you to register (just name + email) 
                to unlock your remaining 2 days. After that, continue with 
                AI Signals for <b style="color: #00FF88;">$9/week</b>, or upgrade to 
                real-money mode for <b style="color: #00FF88;">$99</b> (discounted from $120 for early adopters).
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("I'M READY — LET'S GO", use_container_width=True, type="primary"):
            if 'anonymous_start_date' not in st.session_state:
                st.session_state.anonymous_start_date = datetime.now()
                st.session_state.anonymous_id = f"guest_{random.randint(1000, 9999)}"
                st.session_state.portfolio = Portfolio(user_id=st.session_state.anonymous_id)
            st.session_state.show_landing = False
            st.rerun()


# ==================== LOGIN/REGISTER ====================
def render_auth_page():
    """Render login/register page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center;'>Welcome to Trade With AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>AI-powered stock trading signals</p>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="your@email.com")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login", use_container_width=True)
                
                if submitted:
                    result = user_auth.login(email, password)
                    if result['success']:
                        st.session_state.user_id = result['user_id']
                        st.session_state.user_name = result['name']
                        st.session_state.subscription_type = result['subscription_type']
                        st.session_state.portfolio = portfolio_manager.get_portfolio(result['user_id'])
                        st.success("Logged in successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(result['error'])
        
        with tab2:
            with st.form("register_form"):
                name = st.text_input("Full Name", placeholder="John Doe")
                email = st.text_input("Email", placeholder="your@email.com")
                password = st.text_input("Password", type="password", help="Min 6 characters")
                confirm_password = st.text_input("Confirm Password", type="password")
                
                st.markdown("### 🎁 Free Trial")
                st.markdown(f"- {PRICING['free_trial_days']} days FREE access")
                st.markdown("- $10,000 virtual cash to start")
                st.markdown("- Real-time market data")
                st.markdown("- AI trading signals")
                
                submitted = st.form_submit_button("Start Free Trial", use_container_width=True)
                
                if submitted:
                    if password != confirm_password:
                        st.error("Passwords don't match")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        result = user_auth.register(name, email, password)
                        if result['success']:
                            st.session_state.user_id = result['user_id']
                            st.session_state.user_name = result['name']
                            st.session_state.subscription_type = 'trial'
                            st.session_state.portfolio = Portfolio(user_id=result['user_id'])
                            portfolio_manager.portfolios[result['user_id']] = st.session_state.portfolio
                            st.success(f"Welcome {name}! Your {PRICING['free_trial_days']}-day trial has started!")
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(result['error'])


# ==================== TRIAL ENDING PROMPT ====================
def render_trial_ending_prompt():
    """Show registration prompt after 3-day anonymous trial"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(255,217,61,0.1), rgba(0,212,255,0.1)); 
                    padding: 40px; border-radius: 16px; text-align: center; 
                    border: 1px solid rgba(255,217,61,0.3); margin: 40px 0;">
            <h2 style="color: #FFD93D;">YOUR TRIAL EXPERIENCE CONTINUES</h2>
            <p style="color: #E8E8E8; font-size: 16px;">
                You've spent 3 days exploring Trade With AI. We hope it's been valuable.
            </p>
            <p style="color: #00D4FF; font-size: 18px; margin: 20px 0;">
                Register now to unlock the remaining 2 days FREE, 
                plus get an exclusive <b style="color: #00FF88;">$21 discount</b> 
                on real-money onboarding.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("quick_register"):
            name = st.text_input("Your Name")
            email = st.text_input("Email Address")
            submitted = st.form_submit_button("CONTINUE MY TRIAL", use_container_width=True)
            
            if submitted:
                if name and email:
                    import secrets as sec
                    random_password = sec.token_urlsafe(8)
                    result = user_auth.register(name, email, random_password)
                    if result['success']:
                        st.session_state.user_id = result['user_id']
                        st.session_state.user_name = name
                        st.session_state.subscription_type = 'trial'
                        portfolio_manager.portfolios[result['user_id']] = st.session_state.portfolio
                        st.success(f"Welcome {name}! Trial extended.")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(result['error'])
                else:
                    st.error("Please fill in both fields")


# ==================== DASHBOARD ====================
def render_dashboard():
    """Main dashboard with market overview"""
    st.markdown("<h1>📊 Market Dashboard</h1>", unsafe_allow_html=True)
    
    # Market overview cards
    st.markdown("### 🌐 Market Overview")
    
    # Top movers
    col1, col2, col3, col4 = st.columns(4)
    
    major_indices = [
        ("^GSPC", "S&P 500"),
        ("^DJI", "Dow Jones"),
        ("^IXIC", "NASDAQ"),
        ("^RUT", "Russell 2000")
    ]
    
    for i, (symbol, name) in enumerate(major_indices):
        with [col1, col2, col3, col4][i]:
            quote = trading_engine.get_realtime_quote(symbol)
            if quote:
                change_pct = quote['change_pct']
                color = "#00FF88" if change_pct >= 0 else "#FF4757"
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{name}</h4>
                    <h2 style="color: {color}">${quote['price']:,.2f}</h2>
                    <p style="color: {color}">{change_pct:+.2f}%</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.divider()
    
    # Top Gainers Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔥 TOP DAILY GAINERS")
        daily_gainers = trading_engine.get_top_gainers(DEFAULT_TICKERS, period="1d", top_n=5)
        for g in daily_gainers:
            st.markdown(f"""
            <div style="background:#1A1F2E; padding:10px; border-radius:8px; margin:5px 0; 
                        border-left:3px solid #00FF88; display:flex; justify-content:space-between;">
                <span style="color:#00D4FF;"><b>{g['ticker']}</b></span>
                <span style="color:#00FF88;">+{g['change_pct']:.2f}%</span>
                <span style="color:#888;">${g['price']:.2f}</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📈 TOP WEEKLY GAINERS")
        weekly_gainers = trading_engine.get_top_weekly_gainers(DEFAULT_TICKERS, top_n=5)
        for g in weekly_gainers:
            st.markdown(f"""
            <div style="background:#1A1F2E; padding:10px; border-radius:8px; margin:5px 0; 
                        border-left:3px solid #FFD93D; display:flex; justify-content:space-between;">
                <span style="color:#00D4FF;"><b>{g['ticker']}</b></span>
                <span style="color:#FFD93D;">+{g['weekly_change_pct']:.2f}%</span>
                <span style="color:#888;">${g['price']:.2f}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # AI Opportunities
    st.markdown("### 🤖 AI Top Opportunities")
    
    with st.spinner("Scanning for opportunities..."):
        opportunities = trading_engine.scan_for_opportunities(DEFAULT_TICKERS[:8])
    
    if opportunities:
        for opp in opportunities[:5]:
            col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 1])
            
            with col1:
                signal_color = "#00FF88" if opp['signal'] == 'BUY' else "#FF4757"
                st.markdown(f"<span class='signal-{opp['signal'].lower()}'>{opp['signal']}</span>", unsafe_allow_html=True)
            
            with col2:
                st.write(f"**{opp['ticker']}**")
                st.caption(f"Confidence: {opp['confidence']}%")
            
            with col3:
                st.write(f"${opp['price']:.2f}")
            
            with col4:
                change = opp['change_1d']
                color = "#00FF88" if change >= 0 else "#FF4757"
                st.markdown(f"<span style='color:{color}'>{change:+.2f}%</span>", unsafe_allow_html=True)
            
            with col5:
                if st.button("View", key=f"view_{opp['ticker']}"):
                    st.session_state.selected_ticker = opp['ticker']
                    st.rerun()
    
    st.divider()
    
    # Watchlist
    st.markdown("### 📋 Watchlist")
    
    watchlist_data = []
    for ticker in DEFAULT_TICKERS[:8]:
        quote = trading_engine.get_realtime_quote(ticker)
        if quote:
            watchlist_data.append({
                "Symbol": ticker,
                "Price": f"${quote['price']:.2f}",
                "Change": f"{quote['change_pct']:+.2f}%",
                "Volume": f"{quote['volume']/1e6:.1f}M"
            })
    
    if watchlist_data:
        df = pd.DataFrame(watchlist_data)
        st.dataframe(df, use_container_width=True, hide_index=True)


# ==================== SEARCH PAGE ====================
def render_search_page():
    """Search and analyze stocks"""
    st.markdown("<h1>🔍 Stock Search</h1>", unsafe_allow_html=True)
    
    # Search input
    search_ticker = st.text_input("Enter ticker symbol", value=st.session_state.selected_ticker).upper()
    
    if search_ticker:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Quick quote
            quote = trading_engine.get_realtime_quote(search_ticker)
            if quote:
                st.markdown("### 📈 Quote")
                
                change_pct = quote['change_pct']
                color = "#00FF88" if change_pct >= 0 else "#FF4757"
                
                st.metric("Price", f"${quote['price']:.2f}")
                st.markdown(f"<p style='color:{color}; font-size:24px;'>{change_pct:+.2f}%</p>", unsafe_allow_html=True)
                
                st.write(f"**Open:** ${quote['open']:.2f}")
                st.write(f"**High:** ${quote['high']:.2f}")
                st.write(f"**Low:** ${quote['low']:.2f}")
                st.write(f"**Prev Close:** ${quote['previous_close']:.2f}")
                st.write(f"**Volume:** {quote['volume']/1e6:.2f}M")
                
                # Advanced Multi-Panel Chart
                df = trading_engine.get_stock_data(search_ticker, period="1mo")
                if df is not None:
                    df = trading_engine.calculate_indicators(df)
                    
                    # Create multi-panel chart
                    from plotly.subplots import make_subplots
                    
                    fig = make_subplots(
                        rows=4, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.05,
                        row_heights=[0.5, 0.2, 0.2, 0.1],
                        subplot_titles=('', 'RSI', 'MACD', 'Volume')
                    )
                    
                    # Panel 1: Candlestick with Bollinger Bands
                    fig.add_trace(go.Candlestick(
                        x=df.index,
                        open=df['Open'],
                        high=df['High'],
                        low=df['Low'],
                        close=df['Close'],
                        name="Price",
                        increasing_line_color='#00FF88',
                        decreasing_line_color='#FF4757',
                        increasing_fillcolor='#00FF88',
                        decreasing_fillcolor='#FF4757'
                    ), row=1, col=1)
                    
                    # Bollinger Bands
                    fig.add_trace(go.Scatter(
                        x=df.index, y=df['BB_Upper'],
                        line=dict(color='#FFD93D', width=1),
                        name="BB Upper", hoverinfo='skip'
                    ), row=1, col=1)
                    
                    fig.add_trace(go.Scatter(
                        x=df.index, y=df['BB_Lower'],
                        line=dict(color='#FFD93D', width=1),
                        name="BB Lower", hoverinfo='skip',
                        fill='tonexty', fillcolor='rgba(255,217,61,0.1)'
                    ), row=1, col=1)
                    
                    # SMA lines
                    fig.add_trace(go.Scatter(
                        x=df.index, y=df['SMA_20'],
                        line=dict(color='#00D4FF', width=1.5),
                        name="SMA 20"
                    ), row=1, col=1)
                    
                    fig.add_trace(go.Scatter(
                        x=df.index, y=df['SMA_50'],
                        line=dict(color='#7B2FFF', width=1.5),
                        name="SMA 50"
                    ), row=1, col=1)
                    
                    # Panel 2: RSI
                    colors_rsi = ['#00FF88' if r >= 50 else '#FF4757' for r in df['RSI']]
                    fig.add_trace(go.Scatter(
                        x=df.index, y=df['RSI'],
                        line=dict(color='#FFD93D', width=2),
                        name="RSI", fill='tozeroy',
                        fillcolor='rgba(255,217,61,0.2)'
                    ), row=2, col=1)
                    
                    # RSI levels
                    fig.add_hline(y=70, line_dash="dash", line_color="#FF4757", row=2, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="#00FF88", row=2, col=1)
                    fig.add_hline(y=50, line_dash="dot", line_color="#888", row=2, col=1)
                    
                    # Panel 3: MACD
                    colors_macd = ['#00FF88' if m >= 0 else '#FF4757' for m in df['MACD_Hist']]
                    fig.add_trace(go.Bar(
                        x=df.index, y=df['MACD_Hist'],
                        marker_color=colors_macd,
                        name="MACD Hist"
                    ), row=3, col=1)
                    
                    fig.add_trace(go.Scatter(
                        x=df.index, y=df['MACD'],
                        line=dict(color='#00D4FF', width=2),
                        name="MACD"
                    ), row=3, col=1)
                    
                    fig.add_trace(go.Scatter(
                        x=df.index, y=df['MACD_Signal'],
                        line=dict(color='#FF6B6B', width=2),
                        name="Signal"
                    ), row=3, col=1)
                    
                    # Panel 4: Volume
                    colors_vol = ['#00FF88' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#FF4757' for i in range(len(df))]
                    fig.add_trace(go.Bar(
                        x=df.index, y=df['Volume'],
                        marker_color=colors_vol,
                        name="Volume", opacity=0.7
                    ), row=4, col=1)
                    
                    # Update layout
                    fig.update_layout(
                        template="plotly_dark",
                        height=700,
                        paper_bgcolor='#0A0E17',
                        plot_bgcolor='#0A0E17',
                        font=dict(color='#E8E8E8'),
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        ),
                        xaxis_rangeslider_visible=False
                    )
                    
                    # Update all axes
                    fig.update_xaxes(showgrid=True, gridcolor='#2D3748', row=4, col=1)
                    fig.update_yaxes(showgrid=True, gridcolor='#2D3748')
                    fig.update_yaxes(range=[0, 100], row=2, col=1)  # RSI scale
                    
                    st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Technical Analysis
            st.markdown("### 📊 Technical Analysis")
            
            if df is not None:
                signals = trading_engine.generate_signals(df)
                
                # Signal badge
                signal = signals['signal']
                confidence = signals['confidence']
                signal_color = "#00FF88" if signal == "BUY" else ("#FF4757" if signal == "SELL" else "#FFD93D")
                
                st.markdown(f"""
                <div style="background:#1A1F2E; padding:20px; border-radius:12px; text-align:center;">
                    <h2 style="color:{signal_color}; margin:0;">{signal}</h2>
                    <p style="color:#888;">Confidence: {confidence}%</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Reasons
                st.markdown("**Reasons:**")
                for reason in signals.get('reasons', []):
                    st.write(f"• {reason}")
                
                # Technical indicators
                st.markdown("### 📉 Indicators")
                
                ind_col1, ind_col2, ind_col3 = st.columns(3)
                
                with ind_col1:
                    rsi = signals['indicators']['rsi']
                    rsi_color = "#00FF88" if rsi < 30 else ("#FF4757" if rsi > 70 else "#FFD93D")
                    st.metric("RSI (14)", f"{rsi:.1f}")
                
                with ind_col2:
                    macd = signals['indicators']['macd']
                    st.metric("MACD", f"{macd:.4f}")
                
                with ind_col3:
                    stoch = signals['indicators']['stoch_k']
                    st.metric("Stochastic", f"{stoch:.1f}")
                
                # ML Prediction - Requires AI Access
                st.markdown("### 🤖 AI Prediction")
                
                if not has_ai_access():
                    show_access_required()
                else:
                    with st.spinner("Running ML model..."):
                        prediction = predictor.get_prediction_for_ticker(search_ticker)
                    
                    if 'error' not in prediction:
                        rec = prediction['recommendation']
                        rec_color = "#00FF88" if "BUY" in rec else ("#FF4757" if "SELL" in rec else "#FFD93D")
                        
                        st.markdown(f"""
                        <div style="background:#1A1F2E; padding:20px; border-radius:12px; text-align:center;">
                            <h3 style="color:{rec_color}; margin:0;">{rec.replace('_', ' ')}</h3>
                            <p>Bullish Score: {prediction['bullish_score']:.0f} | Bearish Score: {prediction['bearish_score']:.0f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Trade buttons
                        st.markdown("### 💰 Quick Trade")
                        trade_col1, trade_col2 = st.columns(2)
                        
                        with trade_col1:
                            shares = st.number_input("Shares", min_value=1, max_value=100, value=10, key="trade_shares")
                            total = shares * quote['price']
                            st.info(f"Total: ${total:,.2f}")
                            
                        with trade_col2:
                            if st.button("🟢 BUY", use_container_width=True, type="primary"):
                                result = st.session_state.portfolio.execute_buy(
                                    search_ticker, shares, quote['price']
                                )
                                if result['success']:
                                    st.success(f"Bought {shares} shares of {search_ticker}")
                                    portfolio_manager.save_portfolio(st.session_state.user_id or "guest")
                                else:
                                    st.error(result.get('error', 'Trade failed'))
                            
                            if st.button("🔴 SELL", use_container_width=True):
                                result = st.session_state.portfolio.execute_sell(
                                    search_ticker, shares, quote['price']
                                )
                                if result['success']:
                                    st.success(f"Sold {shares} shares of {search_ticker}")
                                    portfolio_manager.save_portfolio(st.session_state.user_id or "guest")
                                else:
                                    st.error(result.get('error', 'No position to sell'))


# ==================== PORTFOLIO PAGE ====================
def render_portfolio_page():
    """Display and manage portfolio"""
    st.markdown("<h1>💼 Portfolio</h1>", unsafe_allow_html=True)
    
    portfolio = st.session_state.portfolio
    
    # Portfolio summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💵 Cash", f"${portfolio.cash:,.2f}")
    
    with col2:
        st.metric("📈 Positions Value", f"${sum(p.market_value for p in portfolio.positions):,.2f}")
    
    with col3:
        pnl = portfolio.total_pnl
        color = "#00FF88" if pnl >= 0 else "#FF4757"
        st.markdown(f"<h3 style='color:{color}'>P/L: ${pnl:,.2f} ({portfolio.total_pnl_pct:+.2f}%)</h3>", unsafe_allow_html=True)
    
    with col4:
        st.metric("💰 Total Value", f"${portfolio.total_value:,.2f}")
    
    st.divider()
    
    # Positions table
    st.markdown("### 📊 Open Positions")
    
    if portfolio.positions:
        positions_data = []
        for pos in portfolio.positions:
            quote = trading_engine.get_realtime_quote(pos.ticker)
            if quote:
                pos.current_price = quote['price']
            
            pnl_color = "#00FF88" if pos.unrealized_pnl >= 0 else "#FF4757"
            
            positions_data.append({
                "Symbol": pos.ticker,
                "Shares": pos.shares,
                "Avg Price": f"${pos.entry_price:.2f}",
                "Current": f"${pos.current_price:.2f}",
                "Value": f"${pos.market_value:.2f}",
                "P/L": f"<span style='color:{pnl_color}'>${pos.unrealized_pnl:.2f} ({pos.unrealized_pnl_pct:+.2f}%)</span>"
            })
        
        df = pd.DataFrame(positions_data)
        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
        
        # Close position buttons
        st.markdown("### 🔧 Actions")
        for pos in portfolio.positions:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{pos.ticker}** - {pos.shares} shares")
            with col2:
                if st.button(f"Close {pos.ticker}", key=f"close_{pos.ticker}"):
                    quote = trading_engine.get_realtime_quote(pos.ticker)
                    if quote:
                        result = portfolio.execute_sell(pos.ticker, pos.shares, quote['price'])
                        if result['success']:
                            st.success(f"Closed {pos.ticker} position")
                            portfolio_manager.save_portfolio(st.session_state.user_id or "guest")
                            st.rerun()
    else:
        st.info("No open positions. Start trading to see your portfolio here!")
    
    st.divider()
    
    # Trade history
    st.markdown("### 📜 Trade History")
    
    if portfolio.trade_history:
        history_data = []
        for trade in reversed(portfolio.trade_history[-20:]):
            action_color = "#00FF88" if trade.action == "BUY" else "#FF4757"
            history_data.append({
                "Time": trade.timestamp[:19],
                "Action": f"<span style='color:{action_color}'>{trade.action}</span>",
                "Symbol": trade.ticker,
                "Shares": trade.shares,
                "Price": f"${trade.price:.2f}",
                "Total": f"${trade.total:,.2f}",
                "P/L": f"${trade.pnl:.2f}" if trade.pnl else "-"
            })
        
        df = pd.DataFrame(history_data)
        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info("No trades yet")


# ==================== AI SIGNALS PAGE ====================
def render_ai_signals_page():
    """AI trading signals - Full page chart for user's positions only"""
    st.markdown("<h1>🤖 AI TRADING SIGNALS</h1>", unsafe_allow_html=True)
    
    # Show trial warning if ending soon
    show_trial_ending_warning()
    
    if not has_ai_access():
        show_access_required()
        return
    
    portfolio = st.session_state.portfolio
    owned_tickers = [pos.ticker for pos in portfolio.positions]
    
    if not owned_tickers:
        st.markdown("""
        <div style="background:#1A1F2E; padding:40px; border-radius:12px; text-align:center; margin:40px 0;">
            <h3 style="color:#00D4FF; margin-bottom:20px;">📭 NO POSITIONS YET</h3>
            <p style="color:#888; font-size:16px;">AI signals will appear here once you purchase stocks.</p>
            <p style="color:#888;">Head to the Trade page to start building your portfolio.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Auto-trading toggle
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        auto_trade = st.toggle("🤖 AUTO-TRADING MODE", help="AI will automatically execute trades based on signals")
    with col2:
        max_position_pct = st.slider("Max Position %", 5, 50, 20, key="auto_max_pos")
    with col3:
        stop_loss_pct = st.slider("Stop-Loss %", 2, 20, 10, key="auto_stop_loss")
    
    # Execute auto-trade if enabled
    if auto_trade:
        st.warning("⚠️ AUTO-TRADING ACTIVE")
        run_auto_trade(owned_tickers, max_position_pct, stop_loss_pct)
    
    st.divider()
    
    # Full-page chart for each owned ticker
    for ticker in owned_tickers:
        render_ticker_signal_chart(ticker)


def run_auto_trade(owned_tickers, max_position_pct, stop_loss_pct):
    """Execute smarter auto-trading with cooldowns to prevent rapid buy/sell"""
    portfolio = st.session_state.portfolio
    results = []
    
    # Track last trade times to prevent rapid trading
    if 'last_trade_time' not in st.session_state:
        st.session_state.last_trade_time = {}
    
    # Minimum hold time: 1 hour (prevents frantic trading)
    MIN_HOLD_HOURS = 1
    # Minimum confidence for trades
    MIN_BUY_CONFIDENCE = 75  # Higher threshold
    MIN_SELL_CONFIDENCE = 65
    
    for ticker in owned_tickers:
        df = trading_engine.get_stock_data(ticker, period="3mo")
        if df is None:
            continue
        
        df = trading_engine.calculate_indicators(df)
        signal_data = trading_engine.generate_signals(df)
        
        quote = trading_engine.get_realtime_quote(ticker)
        if not quote:
            continue
        
        position = portfolio.get_position(ticker)
        current_price = quote['price']
        
        # Check minimum hold time
        if position and hasattr(position, 'entry_date'):
            try:
                entry_time = datetime.fromisoformat(position.entry_date)
                hours_held = (datetime.now() - entry_time).total_seconds() / 3600
                if hours_held < MIN_HOLD_HOURS and signal_data['signal'] != 'STRONG_SELL':
                    # Skip if held less than min time (unless strong sell signal)
                    continue
            except:
                pass
        
        # STOP-LOSS check (highest priority)
        if position:
            loss_pct = ((current_price - position.entry_price) / position.entry_price) * 100
            if loss_pct <= -stop_loss_pct:
                result = portfolio.execute_sell(ticker, position.shares, current_price)
                if result['success']:
                    results.append(f"STOP-LOSS: {ticker} ({loss_pct:.1f}%)")
                    st.session_state.last_trade_time[ticker] = datetime.now()
                    portfolio_manager.save_portfolio(st.session_state.user_id or "guest")
                continue
        
        # SELL signals - require higher confidence AND minimum hold
        if signal_data['signal'] == 'SELL' and signal_data['confidence'] >= MIN_SELL_CONFIDENCE and position:
            # Only sell if profit OR loss exceeds 2% (avoid selling at tiny loss)
            pnl_pct = ((current_price - position.entry_price) / position.entry_price) * 100
            if pnl_pct > 1.0 or pnl_pct < -2.0:  # Either gain >1% or loss >2%
                result = portfolio.execute_sell(ticker, position.shares, current_price)
                if result['success']:
                    pnl_emoji = "+" if pnl_pct > 0 else ""
                    results.append(f"SOLD {ticker} @ ${current_price:.2f} ({pnl_emoji}{pnl_pct:.1f}%)")
                    st.session_state.last_trade_time[ticker] = datetime.now()
                    portfolio_manager.save_portfolio(st.session_state.user_id or "guest")
                continue
        
        # BUY signals - require very high confidence and no recent buy on this ticker
        if signal_data['signal'] == 'BUY' and signal_data['confidence'] >= MIN_BUY_CONFIDENCE and not position:
            # Check cooldown - no buy in last 4 hours for same ticker
            if ticker in st.session_state.last_trade_time:
                time_since_last = (datetime.now() - st.session_state.last_trade_time[ticker]).total_seconds() / 3600
                if time_since_last < 4:
                    continue
            
            # Calculate position size based on confidence
            # Higher confidence = larger position
            confidence_multiplier = signal_data['confidence'] / 100
            actual_max_pct = max_position_pct * confidence_multiplier
            
            max_investment = portfolio.total_value * (actual_max_pct / 100)
            shares = int(max_investment / current_price)
            
            if shares > 0 and portfolio.cash >= (shares * current_price * 1.01):
                result = portfolio.execute_buy(ticker, shares, current_price)
                if result['success']:
                    results.append(f"BOUGHT {shares} {ticker} @ ${current_price:.2f} ({signal_data['confidence']}%)")
                    st.session_state.last_trade_time[ticker] = datetime.now()
                    portfolio_manager.save_portfolio(st.session_state.user_id or "guest")
    
    # Show results - quiet if no trades
    if results:
        st.success(f"Auto-trade executed: {' | '.join(results[:3])}")
    else:
        st.info("Watching market... holding positions (no signals strong enough)")


def render_ticker_signal_chart(ticker):
    """Render full-page chart for a single ticker"""
    
    # Get position info
    portfolio = st.session_state.portfolio
    position = portfolio.get_position(ticker)
    
    # Get data
    df = trading_engine.get_stock_data(ticker, period="3mo")
    if df is None:
        st.error(f"Could not load data for {ticker}")
        return
    
    df = trading_engine.calculate_indicators(df)
    signals = trading_engine.generate_signals(df)
    
    # Get real-time quote
    quote = trading_engine.get_realtime_quote(ticker)
    current_price = quote['price'] if quote else df['Close'].iloc[-1]
    
    # Ticker header with stats
    pnl_color = "#00FF88" if position and position.unrealized_pnl >= 0 else "#FF4757"
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        st.markdown(f"<h2 style='color:#00D4FF; margin-bottom:5px;'>{ticker}</h2>", unsafe_allow_html=True)
        if position:
            st.markdown(f"<p style='color:{pnl_color}; margin:0;'>P/L: ${position.unrealized_pnl:,.2f} ({position.unrealized_pnl_pct:+.2f}%)</p>", unsafe_allow_html=True)
    with col2:
        signal_color = "#00FF88" if signals['signal'] == 'BUY' else ("#FF4757" if signals['signal'] == 'SELL' else "#FFD93D")
        st.markdown(f"<p style='color:#888; font-size:12px; margin:0;'>SIGNAL</p><h4 style='color:{signal_color}; margin:0;'>{signals['signal']}</h4>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<p style='color:#888; font-size:12px; margin:0;'>CONFIDENCE</p><h4 style='color:#00D4FF; margin:0;'>{signals['confidence']}%</h4>", unsafe_allow_html=True)
    with col4:
        change_color = "#00FF88" if quote['change_pct'] >= 0 else "#FF4757"
        st.markdown(f"<p style='color:#888; font-size:12px; margin:0;'>PRICE</p><h4 style='color:{change_color}; margin:0;'>${current_price:.2f}</h4>", unsafe_allow_html=True)
    
    # Side data (left + right panels around chart)
    col_left, col_chart, col_right = st.columns([1, 6, 1])
    
    with col_left:
        # Left stats panel
        st.markdown("<p style='color:#888; font-size:11px; margin:0;'>RSI</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#00D4FF; font-size:14px; margin:0;'>{signals['indicators']['rsi']:.1f}</p>", unsafe_allow_html=True)
        
        st.markdown("<p style='color:#888; font-size:11px; margin:10px 0 0;'>MACD</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#00D4FF; font-size:14px; margin:0;'>{signals['indicators']['macd']:.4f}</p>", unsafe_allow_html=True)
        
        st.markdown("<p style='color:#888; font-size:11px; margin:10px 0 0;'>STOCH</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#00D4FF; font-size:14px; margin:0;'>{signals['indicators']['stoch_k']:.1f}</p>", unsafe_allow_html=True)
    
    with col_right:
        # Right stats panel
        if quote:
            st.markdown(f"<p style='color:#888; font-size:11px; margin:0;'>HIGH</p><p style='color:#00FF88; font-size:14px; margin:0;'>${quote['high']:.2f}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#888; font-size:11px; margin:10px 0 0;'>LOW</p><p style='color:#FF4757; font-size:14px; margin:0;'>${quote['low']:.2f}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#888; font-size:11px; margin:10px 0 0;'>VOL</p><p style='color:#00D4FF; font-size:14px; margin:0;'>{quote['volume']/1e6:.1f}M</p>", unsafe_allow_html=True)
    
    with col_chart:
        # Full-width chart with sharp thin lines
        fig = go.Figure()
        
        # Price line (sharp, thin)
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'],
            line=dict(color='#00D4FF', width=1.5),
            name="Price"
        ))
        
        # SMA lines (thin)
        fig.add_trace(go.Scatter(
            x=df.index, y=df['SMA_20'],
            line=dict(color='#FFD93D', width=1),
            name="SMA 20"
        ))
        
        fig.add_trace(go.Scatter(
            x=df.index, y=df['SMA_50'],
            line=dict(color='#7B2FFF', width=1),
            name="SMA 50"
        ))
        
        # Bollinger Bands (thin)
        fig.add_trace(go.Scatter(
            x=df.index, y=df['BB_Upper'],
            line=dict(color='#888', width=0.5),
            name="BB Upper",
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=df.index, y=df['BB_Lower'],
            line=dict(color='#888', width=0.5),
            name="BB Lower",
            fill='tonexty',
            fillcolor='rgba(255,217,61,0.05)',
            showlegend=False
        ))
        
        fig.update_layout(
            template="plotly_dark",
            height=350,
            paper_bgcolor='#0A0E17',
            plot_bgcolor='#0A0E17',
            font=dict(color='#888', size=10),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=10)
            ),
            margin=dict(l=0, r=0, t=30, b=20),
            xaxis=dict(showgrid=True, gridcolor='#1A1F2E'),
            yaxis=dict(showgrid=True, gridcolor='#1A1F2E')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Bottom indicator strip
    col_rsi, col_macd, col_volume = st.columns(3)
    
    with col_rsi:
        # RSI mini chart
        fig_rsi = go.Figure()
        rsi_colors = ['#00FF88' if r >= 50 else '#FF4757' for r in df['RSI']]
        fig_rsi.add_trace(go.Scatter(
            x=df.index, y=df['RSI'],
            line=dict(color='#00D4FF', width=1),
            fill='tozeroy',
            fillcolor='rgba(0,212,255,0.1)'
        ))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="#FF4757", line_width=0.5)
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="#00FF88", line_width=0.5)
        fig_rsi.update_layout(
            template="plotly_dark",
            height=120,
            paper_bgcolor='#0A0E17',
            plot_bgcolor='#0A0E17',
            showlegend=False,
            margin=dict(l=0, r=0, t=10, b=10),
            title=dict(text="RSI", font=dict(size=10, color='#888'))
        )
        st.plotly_chart(fig_rsi, use_container_width=True)
    
    with col_macd:
        # MACD mini chart
        fig_macd = go.Figure()
        colors = ['#00FF88' if v >= 0 else '#FF4757' for v in df['MACD_Hist']]
        fig_macd.add_trace(go.Bar(x=df.index, y=df['MACD_Hist'], marker_color=colors))
        fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD'], line=dict(color='#00D4FF', width=1)))
        fig_macd.update_layout(
            template="plotly_dark",
            height=120,
            paper_bgcolor='#0A0E17',
            plot_bgcolor='#0A0E17',
            showlegend=False,
            margin=dict(l=0, r=0, t=10, b=10),
            title=dict(text="MACD", font=dict(size=10, color='#888'))
        )
        st.plotly_chart(fig_macd, use_container_width=True)
    
    with col_volume:
        # Volume mini chart
        fig_vol = go.Figure()
        colors = ['#00FF88' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#FF4757' for i in range(len(df))]
        fig_vol.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors))
        fig_vol.update_layout(
            template="plotly_dark",
            height=120,
            paper_bgcolor='#0A0E17',
            plot_bgcolor='#0A0E17',
            showlegend=False,
            margin=dict(l=0, r=0, t=10, b=10),
            title=dict(text="Volume", font=dict(size=10, color='#888'))
        )
        st.plotly_chart(fig_vol, use_container_width=True)
    
    # Quick actions
    if position:
        action_col1, action_col2, action_col3 = st.columns([1, 1, 2])
        with action_col1:
            shares_to_close = st.number_input("Shares to sell", min_value=1, max_value=int(position.shares), value=int(position.shares), key=f"close_shares_{ticker}")
        with action_col2:
            if st.button(f"🔴 SELL {shares_to_close} SHARES", key=f"sell_btn_{ticker}", use_container_width=True):
                result = portfolio.execute_sell(ticker, shares_to_close, current_price)
                if result['success']:
                    st.success(f"Sold {shares_to_close} shares of {ticker}")
                    portfolio_manager.save_portfolio(st.session_state.user_id or "guest")
                    st.rerun()
    
    st.divider()


# ==================== TRADE PAGE ====================
def render_trade_page():
    """Manual trading interface"""
    st.markdown("<h1>📈 Trade</h1>", unsafe_allow_html=True)
    
    portfolio = st.session_state.portfolio
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🔍 Search Stock")
        ticker = st.text_input("Ticker Symbol", value=st.session_state.selected_ticker).upper()
        
        if ticker:
            quote = trading_engine.get_realtime_quote(ticker)
            if quote:
                st.success(f"**{ticker}** - ${quote['price']:.2f}")
                
                # Position check
                position = portfolio.get_position(ticker)
                if position:
                    st.info(f"You own: {position.shares} shares @ ${position.entry_price:.2f}")
    
    with col2:
        st.markdown("### 💰 Quick Trade")
        
        action = st.radio("Action", ["BUY", "SELL"], horizontal=True)
        
        shares = st.number_input("Number of Shares", min_value=1, max_value=1000, value=10)
        
        if ticker and 'quote' in dir() and quote:
            total = shares * quote['price']
            st.metric("Estimated Cost", f"${total:,.2f}")
            
            if st.button(f"{'🟢' if action == 'BUY' else '🔴'} {action} {ticker}", use_container_width=True):
                if action == "BUY":
                    result = portfolio.execute_buy(ticker, shares, quote['price'])
                else:
                    result = portfolio.execute_sell(ticker, shares, quote['price'])
                
                if result['success']:
                    st.success(f"{action} order executed!")
                    st.write(f"Total: ${result.get('total', result.get('proceeds')):,.2f}")
                    portfolio_manager.save_portfolio(st.session_state.user_id or "guest")
                else:
                    st.error(result.get('error', 'Trade failed'))
    
    st.divider()
    
    # Market orders
    st.markdown("### 📋 Market Overview")
    
    # Mini watchlist for quick trading
    watchlist = st.multiselect("Select stocks to track", DEFAULT_TICKERS, default=["AAPL", "GOOGL", "MSFT"])
    
    for tick in watchlist:
        quote = trading_engine.get_realtime_quote(tick)
        if quote:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{tick}**")
                st.caption(f"${quote['price']:.2f}")
            with col2:
                change = quote['change_pct']
                color = "#00FF88" if change >= 0 else "#FF4757"
                st.markdown(f"<span style='color:{color}'>{change:+.2f}%</span>", unsafe_allow_html=True)
            with col3:
                if st.button("Trade", key=f"trade_{tick}"):
                    st.session_state.selected_ticker = tick
                    st.rerun()


# ==================== SUBSCRIBE PAGE ====================
def render_subscribe_page():
    """Subscription plans and billing"""
    st.markdown("<h1>SUBSCRIPTION PLANS</h1>", unsafe_allow_html=True)
    
    # Trial status
    if st.session_state.user_id and st.session_state.subscription_type == 'trial':
        status = user_auth.check_trial_status(st.session_state.user_id)
        if not status.get('active'):
            st.warning("Your free trial has ended. Subscribe below to continue AI signals!")
    
    st.markdown("### CHOOSE YOUR PLAN")
    
    plans = subscription_manager.get_available_plans()
    
    cols = st.columns(len(plans))
    
    for i, plan in enumerate(plans):
        with cols[i]:
            # Plan card
            st.markdown(f"""
            <div style="background:#1A1F2E; padding:20px; border-radius:12px; min-height:380px; border:1px solid rgba(0,212,255,0.3);">
                <h3 style="color:#00D4FF; text-transform:uppercase; letter-spacing:1px;">{plan['name']}</h3>
                <h2 style="color:#00D4FF; margin:10px 0;">${plan['price']}</h2>
                <p style="color:#888;">/{plan['period']}</p>
                <hr style="border-color:#2D3748; margin:15px 0;">
            </div>
            """, unsafe_allow_html=True)
            
            # Features
            for feature in plan['features']:
                st.markdown(f"<div style='color:#E8E8E8; padding:4px 0;'>✓ {feature}</div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button(f"SUBSCRIBE", key=f"sub_{plan['id']}", use_container_width=True):
                if not stripe_manager.enabled:
                    st.warning("Stripe payments not yet configured. Add your API keys to enable.")
                    st.info("Set STRIPE_SECRET_KEY in Streamlit Cloud secrets to activate payments.")
                    continue
                
                # Create Stripe checkout session
                customer_email = st.session_state.user_email if hasattr(st.session_state, 'user_email') else None
                
                with st.spinner("Creating checkout session..."):
                    result = stripe_manager.create_checkout_session(plan['id'], customer_email)
                
                if result['success']:
                    st.success(f"Redirecting to Stripe Checkout...")
                    st.markdown(f"**[Click here to pay ${plan['price']}]({result['url']})**")
                    st.markdown(f"""
                    <script>
                        window.open('{result['url']}', '_blank');
                    </script>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"Payment setup failed: {result.get('error')}")
                    st.info("Try again or contact support.")
                
                if plan['id'] == 'real_money':
                    st.warning("Real money trading requires additional identity verification and SEC compliance.")
    
    st.divider()
    
    # Pricing breakdown
    st.markdown("### PRICING BREAKDOWN")
    
    pricing_data = [
        {"Plan": "AI Signals (Weekly)", "Price": f"${PRICING['ai_signals_weekly']}/week"},
        {"Plan": "AI Signals (Monthly)", "Price": f"${PRICING['ai_signals_monthly']}/month"},
        {"Plan": "Newsletter Only", "Price": f"${PRICING['newsletter_monthly']}/month"},
        {"Plan": "Real Money Onboarding", "Price": f"${PRICING['real_money_onboarding']} one-time"},
        {"Plan": "Gains Fee (Real Money)", "Price": f"{PRICING['gains_percentage']}% bi-weekly"},
    ]
    
    st.markdown("""
    <div style="background:#1A1F2E; padding:20px; border-radius:12px; border:1px solid rgba(0,212,255,0.2);">
    """, unsafe_allow_html=True)
    st.table(pd.DataFrame(pricing_data))
    st.markdown("</div>", unsafe_allow_html=True)


# ==================== ACCOUNT PAGE ====================
def render_account_page():
    """User account settings"""
    st.markdown("<h1>ACCOUNT</h1>", unsafe_allow_html=True)
    
    if st.session_state.user_id:
        user = user_auth.get_user(st.session_state.user_id)
        if user:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("### PROFILE")
                st.markdown(f"""
                <div style="background:#1A1F2E; padding:20px; border-radius:12px; border:1px solid rgba(0,212,255,0.2);">
                    <p style="color:#888; font-size:12px; margin:0;">NAME</p>
                    <p style="color:#00D4FF; font-size:18px; margin:5px 0;">{user.name}</p>
                    <p style="color:#888; font-size:12px; margin:10px 0 0;">EMAIL</p>
                    <p style="color:#00D4FF; font-size:14px; margin:5px 0;">{user.email}</p>
                    <p style="color:#888; font-size:12px; margin:10px 0 0;">MEMBER SINCE</p>
                    <p style="color:#E8E8E8; font-size:14px; margin:5px 0;">{user.created_at[:10]}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("### SUBSCRIPTION")
                
                sub_type = user.subscription_type
                if sub_type == 'trial':
                    status = user_auth.check_trial_status(st.session_state.user_id)
                    if status.get('active'):
                        st.markdown(f"""
                        <div style="background:rgba(0,255,136,0.1); padding:20px; border-radius:12px; border:1px solid #00FF88;">
                            <h4 style="color:#00FF88; margin:0;">FREE TRIAL ACTIVE</h4>
                            <p style="color:#E8E8E8; margin:5px 0;">{status.get('days_remaining')} days remaining</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style="background:rgba(255,71,87,0.1); padding:20px; border-radius:12px; border:1px solid #FF4757;">
                            <h4 style="color:#FF4757; margin:0;">TRIAL EXPIRED</h4>
                            <p style="color:#E8E8E8; margin:5px 0;">Subscribe to continue using AI signals</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info(f"Current plan: {sub_type}")
                
                st.markdown("### TRADING STATS")
                portfolio = st.session_state.portfolio
                
                stats_data = [
                    {"Metric": "Total Trades", "Value": len(portfolio.trade_history)},
                    {"Metric": "Buy Orders", "Value": len([t for t in portfolio.trade_history if t.action == 'BUY'])},
                    {"Metric": "Sell Orders", "Value": len([t for t in portfolio.trade_history if t.action == 'SELL'])},
                    {"Metric": "Open Positions", "Value": len(portfolio.positions)},
                    {"Metric": "Total P/L", "Value": f"${portfolio.total_pnl:.2f}"},
                ]
                
                st.markdown("""
                <div style="background:#1A1F2E; padding:15px; border-radius:12px; border:1px solid rgba(0,212,255,0.2);">
                """, unsafe_allow_html=True)
                st.table(pd.DataFrame(stats_data))
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Please log in to view your account details.")
    else:
        st.markdown("""
        <div style="background:#1A1F2E; padding:30px; border-radius:12px; text-align:center; border:1px solid rgba(0,212,255,0.2);">
            <h3 style="color:#00D4FF;">NOT LOGGED IN</h3>
            <p style="color:#888;">Please log in or register to view your account</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Demo mode info
    st.divider()
    st.markdown("### DEMO MODE INFO")
    st.markdown("""
    <div style="background:#1A1F2E; padding:20px; border-radius:12px; border:1px solid rgba(0,212,255,0.2);">
        <p style="color:#888;">You're using TradeAI Pro in demo mode with fake money.</p>
        <p style="color:#00D4FF; margin-top:15px;"><b>FEATURES AVAILABLE:</b></p>
        <ul style="color:#E8E8E8;">
            <li>Real-time market data</li>
            <li>AI trading signals</li>
            <li>Technical analysis</li>
            <li>Portfolio tracking</li>
        </ul>
        <p style="color:#00D4FF; margin-top:15px;"><b>TO UNLOCK REAL TRADING:</b></p>
        <ul style="color:#E8E8E8;">
            <li>Subscribe to AI Signals for ${}/week</li>
            <li>Or upgrade to Real Money mode for ${} (includes SEC-compliant setup)</li>
        </ul>
    </div>
    """.format(PRICING['ai_signals_weekly'], PRICING['real_money_onboarding']), unsafe_allow_html=True)


# ==================== MAIN ====================
def main():
    """Main application entry point"""
    
    # Show landing page first if user hasn't started yet
    if 'show_landing' not in st.session_state:
        st.session_state.show_landing = True
    
    if st.session_state.show_landing:
        render_landing_page()
        return
    
    # Check if anonymous trial has exceeded 3 days and user hasn't registered
    if 'anonymous_start_date' in st.session_state and not st.session_state.user_id:
        days_elapsed = (datetime.now() - st.session_state.anonymous_start_date).days
        if days_elapsed >= 3:
            # Show registration prompt
            render_trial_ending_prompt()
            return
    
    # Render sidebar and get current page
    page = render_sidebar()
    
    # Route to appropriate page
    if page == "Dashboard":
        render_dashboard()
    elif page == "Search":
        render_search_page()
    elif page == "Portfolio":
        render_portfolio_page()
    elif page == "AI Signals":
        render_ai_signals_page()
    elif page == "Trade":
        render_trade_page()
    elif page == "Subscribe":
        render_subscribe_page()
    elif page == "Account":
        render_account_page()
    
    # Auto-refresh for demo
    if st.sidebar.toggle("🔄 Auto-refresh"):
        time.sleep(5)
        st.rerun()


if __name__ == "__main__":
    main()
