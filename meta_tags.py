"""
Open Graph / Social Media Meta Tags for Trade With AI
Shows a preview thumbnail when URL is shared
"""
import streamlit as st


def add_meta_tags():
    """Add Open Graph meta tags for social sharing preview"""
    
    # Title and description for the preview
    meta_html = """
    <meta property="og:title" content="Trade With AI - Virtual Stock Trading">
    <meta property="og:description" content="AI-powered stock trading signals with $10K virtual cash. Try instantly, risk-free. Real-time market data, ML predictions, automated trading.">
    <meta property="og:image" content="https://tradeai-signals-ldxpkbbuagvhgvbmqeqcq8.streamlit.app/~git+/static/og-image.png">
    <meta property="og:url" content="https://tradeai-signals-ldxpkbbuagvhgvbmqeqcq8.streamlit.app">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Trade With AI">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Trade With AI">
    <meta name="twitter:description" content="AI stock trading with $10K virtual cash. Risk-free. Real-time.">
    <meta name="twitter:image" content="https://tradeai-signals-ldxpkbbuagvhgvbmqeqcq8.streamlit.app/~git+/static/og-image.png">
    
    <!-- General -->
    <meta name="description" content="Trade With AI - AI-powered stock trading signals. Start with $10K virtual cash. No risk, real market data.">
    <meta name="keywords" content="AI trading, stock signals, paper trading, virtual trading, ML predictions">
    <meta name="author" content="Trade With AI">
    """
    
    st.markdown(meta_html, unsafe_allow_html=True)


def add_thumbnail_instructions():
    """Show instructions for creating thumbnail"""
    st.markdown("""
    ## 📸 THUMBNAIL SETUP
    
    To add a preview thumbnail when sharing your link:
    
    1. **Create an image** (1200x630px recommended)
       - Use Canva.com (free)
       - Or https://og-image.vercel.app (auto-generates)
    
    2. **Save as** `static/og-image.png` in your GitHub repo
    
    3. **Image should show:**
       - "TRADE WITH AI" logo
       - Tagline: "AI-Powered Stock Trading"
       - "$10,000 Virtual Cash" prominently
       - Dark background with neon accents
    
    4. **Commit and push** - auto-deploys
    """)