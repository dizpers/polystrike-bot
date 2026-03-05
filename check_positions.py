"""Check current positions and portfolio status."""
import sys
from config import load_config
from polystrike_client import PolystrikeClient


def main():
    """Display current portfolio status."""
    config = load_config()

    client = PolystrikeClient(
        api_url=config.polystrike_api_url,
        api_key=config.polystrike_api_key
    )

    print("\n" + "="*70)
    print("POLYSTRIKE PORTFOLIO STATUS")
    print("="*70 + "\n")

    # Get portfolio
    portfolio = client.get_portfolio(config.wallet_address)

    if not portfolio:
        print("❌ Failed to fetch portfolio")
        sys.exit(1)

    # Portfolio summary
    event = portfolio.get("event", {})
    prediction = portfolio.get("prediction", {})
    positions = portfolio.get("positions", [])
    portfolio_summary = portfolio.get("portfolio", {})

    print(f"Event: {event.get('title', 'Unknown')}")
    print(f"Current Count: {event.get('current_count', 0)}")
    print(f"Hours Remaining: {event.get('hours_remaining', 0):.1f}")
    print()

    print("--- MODEL FORECAST ---")
    print(f"p5:  {prediction.get('p5', 0)}")
    print(f"p50: {prediction.get('p50', 0)}")
    print(f"p95: {prediction.get('p95', 0)}")
    print()

    print("--- PORTFOLIO SUMMARY ---")
    total_cost = portfolio_summary.get("total_cost", 0)
    current_value = portfolio_summary.get("current_value", 0)
    expected_value = portfolio_summary.get("expected_value", 0)

    print(f"Total Cost:      ${total_cost:.2f}")
    print(f"Current Value:   ${current_value:.2f}")
    print(f"Expected Value:  ${expected_value:.2f}")
    print(f"Unrealized P&L:  ${current_value - total_cost:+.2f}")
    print()

    if not positions:
        print("No active positions")
        return

    print("--- ACTIVE POSITIONS ---")
    print(f"{'Bucket':<12} {'Tokens':<10} {'Entry':<8} {'Current':<8} {'P&L':<12} {'Model':<8} {'Signal':<15}")
    print("-" * 90)

    for pos in positions:
        bucket = pos.get("bucket", "")
        tokens = pos.get("tokens", 0)
        entry_price = pos.get("entry_price", 0)
        current_price = pos.get("current_price", 0)
        pnl_pct = pos.get("pnl_percent", 0)

        analysis = pos.get("analysis", {})
        model_prob = analysis.get("win_probability", 0)
        signal = analysis.get("signal", "")
        recommendation = analysis.get("recommendation", "")

        pnl_str = f"{pnl_pct:+.1f}%"

        print(f"{bucket:<12} {tokens:<10.1f} ${entry_price:<7.2f} ${current_price:<7.2f} {pnl_str:<12} {model_prob:<7.0%} {recommendation:<15}")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
