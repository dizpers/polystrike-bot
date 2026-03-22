#!/usr/bin/env python3
"""
Quick verification script to test bot setup.

Run this after configuring .env to verify everything is working.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import load_config, validate_config
from polystrike_client import PolystrikeClient


def main():
    print("🔍 Polystrike Bot Verification\n")

    # 1. Load and validate config
    print("1. Loading configuration...")
    try:
        config = load_config()
        print("   ✅ Configuration loaded")
    except Exception as e:
        print(f"   ❌ Failed to load config: {e}")
        return False

    # 2. Validate config
    print("\n2. Validating configuration...")
    is_valid, errors = validate_config(config)
    if is_valid:
        print("   ✅ Configuration valid")
    else:
        print("   ❌ Configuration errors:")
        for error in errors:
            print(f"      - {error}")
        return False

    # 3. Test Polystrike API connection
    print("\n3. Testing Polystrike API connection...")
    try:
        client = PolystrikeClient(config.polystrike_api_url, config.polystrike_api_key)
        signals = client.get_signals(bankroll=100.0)
        print(f"   ✅ API connection successful")
        print(f"   📊 Fetched {len(signals)} event(s)")

        # Check for token_ids
        has_token_ids = False
        for event in signals:
            for signal in event.get("signals", []):
                if signal.get("token_id"):
                    has_token_ids = True
                    print(f"   ✅ token_id found in signals")
                    break
            if has_token_ids:
                break

        if not has_token_ids:
            print("   ⚠️  No token_ids found in signals")
            print("      Backend may need to be deployed or market prices need to refresh")

    except Exception as e:
        print(f"   ❌ API connection failed: {e}")
        return False

    # 4. Check dry-run mode
    print("\n4. Checking trading mode...")
    if config.dry_run:
        print("   ✅ DRY_RUN mode enabled (safe for testing)")
    else:
        print("   ⚠️  LIVE trading mode enabled")
        print("      Make sure you have USDC in your wallet!")

    print("\n" + "="*60)
    print("✅ All checks passed! Bot is ready to run.")
    print("="*60)
    print("\nNext steps:")
    print("  - Run in dry-run mode: DRY_RUN=true python3 bot.py")
    print("  - Run tests: pytest")
    print("  - Check positions: python3 check_positions.py")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
