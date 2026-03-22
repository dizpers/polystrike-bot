# Polystrike Trading Bot

Automated trading bot that executes trades on Polymarket based on signals from the Polystrike prediction API.

## Features

- ✅ **Automated Trading**: Executes BUY signals from Polystrike API
- ✅ **Risk Management**: Kelly sizing, stop-loss, position limits
- ✅ **Token ID Support**: Direct trade execution via Polymarket CLOB
- ✅ **Configuration Validation**: Prevents misconfiguration errors
- ✅ **Dry-Run Mode**: Test without real trades
- ✅ **Test Coverage**: Unit and integration tests included

## Quick Start

```bash
# 1. Install dependencies
uv venv && source .venv/bin/activate
uv pip install -e ".[test]"

# 2. Configure
cp .env.example .env
# Edit .env with your API keys

# 3. Verify setup
python3 verify_setup.py

# 4. Run in dry-run mode
DRY_RUN=true python3 bot.py

# 5. Run tests
pytest
```

## Required API Keys

- **Polystrike Pro API**: `ps_pro_xxxxx` ($79/mo) - https://polystrike.xyz
- **Polymarket Wallet**: Private key + address (see setup guide)
- **Telegram Bot** (optional): For trade alerts

## Documentation

- `README_SETUP.md` - Detailed setup instructions
- `IMPLEMENTATION_SUMMARY.md` - Technical implementation details
- `/Users/dizpers/.claude/plans/scalable-napping-oasis.md` - Full implementation plan

## Safety

- Start with `DRY_RUN=true` to test without real trades
- Use dedicated wallet with limited funds
- Start with small bankroll ($100-500)
- Monitor closely for first 24-48 hours

## Support

- Backend issues: Check Polystrike API status
- Bot issues: Run `python3 verify_setup.py`
- Tests: Run `pytest -v` for detailed output
