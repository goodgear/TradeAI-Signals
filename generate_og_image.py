"""
Generate OG image for Trade With AI
Run this once to create the preview thumbnail
"""
import base64
from pathlib import Path


def generate_og_image_html():
    """Generate HTML for OG image that can be screenshotted"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {
            margin: 0;
            padding: 0;
            width: 1200px;
            height: 630px;
            background: linear-gradient(135deg, #0A0E17 0%, #1A1F2E 50%, #0A0E17 100%);
            font-family: 'Arial', sans-serif;
            overflow: hidden;
            position: relative;
        }
        
        /* Grid background */
        body::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: 
                linear-gradient(rgba(0,212,255,0.1) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,212,255,0.1) 1px, transparent 1px);
            background-size: 50px 50px;
        }
        
        .container {
            position: relative;
            padding: 80px;
            z-index: 2;
        }
        
        .logo {
            color: #00D4FF;
            font-size: 24px;
            font-weight: 300;
            letter-spacing: 8px;
            margin-bottom: 30px;
            text-shadow: 0 0 10px #00D4FF;
        }
        
        .title {
            color: #00D4FF;
            font-size: 84px;
            font-weight: 700;
            letter-spacing: 4px;
            line-height: 1;
            margin-bottom: 20px;
            text-shadow: 0 0 20px #00D4FF, 0 0 40px #00D4FF;
        }
        
        .subtitle {
            color: #E8E8E8;
            font-size: 32px;
            font-weight: 300;
            letter-spacing: 2px;
            margin-bottom: 40px;
        }
        
        .highlight {
            display: inline-block;
            background: linear-gradient(135deg, #00D4FF, #7B2FFF);
            color: white;
            padding: 15px 40px;
            border-radius: 50px;
            font-size: 36px;
            font-weight: 600;
            letter-spacing: 2px;
            margin-bottom: 30px;
        }
        
        .features {
            display: flex;
            gap: 30px;
            margin-top: 50px;
        }
        
        .feature {
            color: #00FF88;
            font-size: 20px;
            letter-spacing: 1px;
        }
        
        .feature::before {
            content: '✓ ';
            color: #00FF88;
            font-weight: bold;
        }
        
        /* Decorative elements */
        .glow1 {
            position: absolute;
            top: -100px;
            right: -100px;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, rgba(0,212,255,0.3) 0%, transparent 70%);
            border-radius: 50%;
        }
        
        .glow2 {
            position: absolute;
            bottom: -100px;
            left: -100px;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, rgba(123,47,255,0.3) 0%, transparent 70%);
            border-radius: 50%;
        }
    </style>
    </head>
    <body>
        <div class="glow1"></div>
        <div class="glow2"></div>
        <div class="container">
            <div class="logo">▣ TRADE WITH AI</div>
            <div class="title">AI STOCK<br>SIGNALS</div>
            <div class="subtitle">Real-time intelligence. Zero risk.</div>
            <div class="highlight">$10,000 VIRTUAL CASH</div>
            <div class="features">
                <span class="feature">Real-time Data</span>
                <span class="feature">ML Predictions</span>
                <span class="feature">Auto-Trading</span>
            </div>
        </div>
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    # Save HTML for screenshotting
    html_content = generate_og_image_html()
    
    # Save to static folder
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    
    html_path = static_dir / "og-image.html"
    with open(html_path, "w") as f:
        f.write(html_content)
    
    print(f"✓ Saved HTML to {html_path}")
    print("\n📸 To create your OG image:")
    print("1. Open static/og-image.html in Chrome")
    print("2. Take a screenshot (1200x630)")
    print("3. Save as static/og-image.png")
    print("4. Commit and push to GitHub")
    print("\nOR use an online generator:")
    print("https://og-image.vercel.app")