"""Demo script to show how the bot analyzes signals without trading."""
import sys
from config import load_config
from polystrike_client import PolystrikeClient
from risk_manager import RiskManager


def main():
    """Run a demo analysis of current signals."""
    print("\n" + "="*70)
    print("POLYSTRIKE BOT DEMO - Signal Analysis")
    print("="*70 + "\n")

    try:
        config = load_config()
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        print("\nMake sure you have a .env file with POLYSTRIKE_API_KEY set.")
        print("Copy .env.example to .env and add your API key.")
        sys.exit(1)

    client = PolystrikeClient(
        api_url=config.polystrike_api_url,
        api_key=config.polystrike_api_key
    )

    risk_manager = RiskManager(
        bankroll=config.bankroll,
        max_position_size=config.max_position_size,
        min_edge=config.min_edge,
        stop_loss_pct=config.stop_loss_pct,
        max_portfolio_exposure=config.max_portfolio_exposure,
        min_confidence=config.min_confidence
    )

    print(f"📊 Configuration:")
    print(f"   Bankroll: ${config.bankroll:.2f}")
    print(f"   Max Position: ${config.max_position_size:.2f}")
    print(f"   Min Edge: {config.min_edge:.1%}")
    print(f"   Min Confidence: {config.min_confidence}")
    print()

    print("🔍 Fetching signals from Polystrike API...\n")

    signals = client.get_signals(config.bankroll)

    if not signals:
        print("❌ No signals available")
        print("\nThis could mean:")
        print("  - No active events right now")
        print("  - Market is fairly priced (no edge)")
        print("  - API key issue")
        sys.exit(0)

    print(f"Found {len(signals)} signals\n")
    print("="*70)

    # Analyze each signal
    buy_count = 0
    skip_count = 0

    for signal in signals:
        action = signal.get("action", "SKIP")
        bucket = signal.get("bucket", "")
        event_id = signal.get("event_id", 0)

        if action == "BUY":
            buy_count += 1
            print(f"\n💰 BUY SIGNAL")
        else:
            skip_count += 1
            print(f"\n⏭️  SKIP")

        print(f"   Event: {event_id} | Bucket: {bucket}")
        print(f"   Model Probability: {signal.get('model_prob', 0):.1%}")
        print(f"   Market Price: {signal.get('market_price', 0):.1%}")
        print(f"   Edge: {signal.get('edge', 0):+.1%}")
        print(f"   Expected Value: ${signal.get('ev', 0):+.3f} per $1")
        print(f"   Confidence: {signal.get('confidence', 'UNKNOWN')}")
        print(f"   Suggested Bet: ${signal.get('suggested_bet', 0):.2f}")

        if action == "BUY":
            # Check if risk manager would approve
            should_execute, reason = risk_manager.should_execute_buy(signal, 0.0)
            if should_execute:
                print(f"   ✅ Risk Check: PASS")
            else:
                print(f"   ❌ Risk Check: FAIL - {reason}")

        # Show reasons
        reasons = signal.get("reasons", [])
        if reasons:
            print(f"   Reasons:")
            for r in reasons[:3]:  # Show first 3 reasons
                print(f"     • {r}")

    print("\n" + "="*70)
    print(f"\n📊 Summary:")
    print(f"   BUY signals: {buy_count}")
    print(f"   SKIP signals: {skip_count}")

    if buy_count > 0:
        print(f"\n💡 To execute these signals:")
        print(f"   1. Set DRY_RUN=false in .env")
        print(f"   2. Add your WALLET_PRIVATE_KEY")
        print(f"   3. Run: uv run bot.py")
    else:
        print(f"\n💡 No actionable signals right now.")
        print(f"   The bot will keep monitoring and execute when opportunities arise.")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
