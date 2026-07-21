"""
Quick test for Alpaca API keys — NO storage, just verify.
Run from PowerShell with your keys as env vars (NEVER paste them in chat):

  $env:ALPACA_TEST_KEY = "your_key_id_here"
  $env:ALPACA_TEST_SECRET = "your_secret_here"
  python alpaca_key_test.py

Tests paper (default). Set ALPACA_TEST_LIVE=true to also test live.
"""
import os
import sys

sys.path.insert(0, r"C:\Users\go4de\ai_trading_app")

from alpaca_integration import quick_test


def main():
    print("=" * 60)
    print("Alpaca API Key Verification (no storage)")
    print("=" * 60)
    print()

    key = os.environ.get("ALPACA_TEST_KEY")
    secret = os.environ.get("ALPACA_TEST_SECRET")

    if not key or not secret:
        print("ERROR: Missing env vars.")
        print()
        print("Set them in PowerShell first (replace with your actual keys):")
        print('  $env:ALPACA_TEST_KEY = "PKxxxxxxxxxxxxx"')
        print('  $env:ALPACA_TEST_SECRET = "your_secret_here"')
        print("  python alpaca_key_test.py")
        print()
        print("Get keys at: https://app.alpaca.markets -> Account -> API Keys")
        sys.exit(1)

    print(f"Key prefix: {key[:6]}...{key[-4:]} (length: {len(key)})")
    print(f"Secret length: {len(secret)}")
    print()

    # Test PAPER
    print("--- PAPER TRADING ACCOUNT ---")
    paper = quick_test(key, secret, paper=True)
    if paper["success"]:
        print(f"  [OK] Connected")
        print(f"  Account ID:  {paper['account_id']}")
        print(f"  Status:      {paper['status']}")
        print(f"  Equity:      ${paper['equity']:,.2f}")
        print(f"  Cash:        ${paper['cash']:,.2f}")
        print(f"  Buy Power:   ${paper['buying_power']:,.2f}")
        print(f"  Currency:    {paper['currency']}")
    else:
        print(f"  [FAILED] {paper['error']}")
        print()
        print("Common causes:")
        print("  - Wrong key/secret (check for typos)")
        print("  - Using LIVE key for paper (or vice versa)")
        print("  - Key was regenerated in Alpaca dashboard")
        print("  - Account not yet approved")
        return

    print()

    test_live = os.environ.get("ALPACA_TEST_LIVE", "").lower() == "true"
    if test_live:
        print("--- LIVE TRADING ACCOUNT (REAL MONEY) ---")
        print("  WARNING: this is your live account with real funds.")
        live = quick_test(key, secret, paper=False)
        if live["success"]:
            print(f"  [OK] Connected")
            print(f"  Account ID:  {live['account_id']}")
            print(f"  Equity:      ${live['equity']:,.2f}")
        else:
            print(f"  [FAILED] {live['error']}")
    else:
        print("--- LIVE ACCOUNT (skipped) ---")
        print("  Set $env:ALPACA_TEST_LIVE = 'true' to also test live keys.")

    print()
    print("=" * 60)
    if paper["success"]:
        print("Next: enter these same keys in the app's Account -> Connect Brokerage form.")
        print("Paper keys work with paper=true. Live keys need paper=false.")


if __name__ == "__main__":
    main()
