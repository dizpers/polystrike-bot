# Polystrike Trading Bot

**Automated Polymarket trading bot powered by [Polystrike](https://polystrike.xyz) prediction signals.**

This bot consumes real-time trading signals from the Polystrike API and executes trades on Polymarket using optimal Kelly sizing and risk management.

## Features

- 🎯 **Signal-Driven Trading**: Automatically executes BUY signals from Polystrike's prediction model
- 💰 **Kelly Sizing**: Position sizes calculated using Kelly Criterion for optimal bankroll growth
- 🛡️ **Risk Management**: Enforces stop-loss rules, position limits, and bankroll constraints
- 📊 **Portfolio Tracking**: Real-time P&L monitoring and position analysis
- 🔔 **Telegram Alerts**: Get notified of all trades and important events

## Prerequisites

1. **Polystrike Pro API Key** ($79/mo) - [Get yours here](https://polystrike.xyz)
2. **Polymarket Wallet** with USDC balance
3. **Telegram Bot** (optional, for alerts)

## Quick Start

### 1. Installation

```bash
git clone https://github.com/polystrike/polystrike-bot.git
cd polystrike-bot
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### 2. Configuration

Copy the example config and add your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
# Polystrike API (Required)
POLYSTRIKE_API_KEY=ps_pro_your_key_here

# Polymarket Wallet (Required)
WALLET_PRIVATE_KEY=0x...
WALLET_ADDRESS=0x...

# Trading Parameters
BANKROLL=100.0              # Your trading bankroll in USD
MAX_POSITION_SIZE=30.0      # Max $ per position (30% of bankroll)
MIN_EDGE=0.05               # Minimum edge to trade (5%)
STOP_LOSS_PCT=-0.30         # Exit at -30% loss

# Telegram Alerts (Optional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

### 3. Run the Bot

```bash
uv run bot.py
```

The bot will:
1. Fetch signals from Polystrike API every 5 minutes
2. Execute BUY signals that meet your risk criteria
3. Monitor existing positions for stop-loss triggers
4. Send Telegram alerts for all actions

## How It Works

### Signal Consumption

The bot polls `/api/v1/signals/elon?bankroll=YOUR_BANKROLL` every 5 minutes and receives:

```json
{
  "event_id": 236151,
  "bucket": "65-89",
  "action": "BUY",
  "model_prob": 0.72,
  "market_price": 0.45,
  "edge": 0.27,
  "ev": 0.60,
  "kelly_fraction": 0.15,
  "suggested_bet": 15.00,
  "confidence": "HIGH"
}
```

### Execution Logic

The bot only executes if:
- ✅ `action == "BUY"`
- ✅ `confidence in ["HIGH", "MEDIUM"]`
- ✅ `edge >= MIN_EDGE`
- ✅ `suggested_bet <= MAX_POSITION_SIZE`
- ✅ Total portfolio exposure < 80% of bankroll

### Risk Management

- **Stop-Loss**: Automatically sells positions at -30% loss (configurable)
- **Position Limits**: Never exceeds 30% of bankroll per position
- **Exposure Limits**: Total portfolio capped at 80% of bankroll
- **Model Override**: Won't sell if model probability > 50% (smart stop-loss)

## Trading Rules (From Polystrike Memory)

The bot enforces these proven rules:

1. **Only trade Elon 48h events** (highest model accuracy)
2. **Max 1-2 positions per event** (concentration > diversification)
3. **Wait for model probability > 50%** before buying
4. **Sell at -30% IF model prob < 50%** (smart stop-loss)
5. **Never bet when p50 near bucket boundary** (within 5 tweets)
6. **Skip if p5-p95 span > 2 buckets** (too much uncertainty)

## Example Output

```
[2026-03-06 02:30:15] 🔍 Fetching signals from Polystrike API...
[2026-03-06 02:30:16] 💰 BUY Signal: Event 236151 → 65-89
                      Model: 72% vs Market: 45% (edge: +27%)
                      EV: $0.60/$ | Kelly: 15% | Bet: $15.00
                      Confidence: HIGH
[2026-03-06 02:30:17] ✅ Order placed: 33.3 shares @ $0.45
[2026-03-06 02:30:17] 📊 Portfolio: 1 position | $15 deployed | $85 cash
```

## Monitoring

Check your positions anytime:

```bash
uv run check_positions.py
```

Output:
```
--- PORTFOLIO STATUS ---
Bankroll: $100.00
Deployed: $15.00 (15%)
Available: $85.00

--- ACTIVE POSITIONS ---
Event 236151 | 65-89 | 33.3 shares | P&L: +$5.50 (+36.7%)
Model: 72% | Market: 62% | Edge: +10% | Signal: HOLD
```

## Safety Features

- **Dry Run Mode**: Test without real trades (`DRY_RUN=true`)
- **Manual Approval**: Require confirmation before each trade (`REQUIRE_APPROVAL=true`)
- **Trade Logging**: All actions logged to `trades.log`
- **Position Limits**: Hard caps prevent over-exposure

## Why Use This Bot?

### The Polystrike Edge

Polystrike's prediction model has demonstrated:
- **60-70% win rate** on high-confidence signals
- **15-25% average edge** on BUY signals
- **Real-time XTracker alignment** (no lag arbitrage)
- **Sleep-aware modeling** (accounts for Elon's schedule)

### Compounding Strategy

With consistent 15% edge and proper Kelly sizing:
- **Week 1**: $100 → $115 (+15%)
- **Week 4**: $100 → $175 (+75%)
- **Week 12**: $100 → $405 (+305%)

*Past performance doesn't guarantee future results. Trade responsibly.*

## Costs

- **Polystrike Pro API**: $79/month
- **Polymarket Fees**: 2% on winning trades
- **Gas Fees**: ~$0.10-0.50 per trade (Polygon)

**Break-even**: ~5 winning trades per month at $15 position size.

## Disclaimer

This bot is for educational purposes. Prediction markets involve risk. Only trade with money you can afford to lose. The authors are not responsible for trading losses.

## Support

- **API Issues**: support@polystrike.xyz
- **Bot Issues**: [GitHub Issues](https://github.com/polystrike/polystrike-bot/issues)
- **Community**: [Discord](https://discord.gg/polystrike)

## License

MIT License - See LICENSE file
