# Polystrike Trading Bot - Implementation Summary

## Changes Completed

### 1. Backend Changes (Polystrike API)

**File: `src/ingest/polymarket_fetcher.py`**
- Modified `fetch_market_prices()` to extract `clobTokenIds[0]` from Gamma API
- Added `token_id` to market snapshots data structure

**File: `src/storage/sqlite_handler.py`**
- Added `token_id TEXT` column to `elon_market_snapshots` table schema
- Updated `insert_market_snapshots()` to store token_id
- Updated `get_latest_market_prices()` to return token_id

**File: `src/services/signal_generator.py`**
- Added `token_id: str | None` field to `Signal` dataclass
- Updated `generate_signals()` to extract and pass token_id from market data
- Modified signal creation to include token_id

**File: `src/scripts/migrate_add_token_id.py`** (NEW)
- Created migration script to add `token_id` column to existing databases
- Idempotent - safe to run multiple times

### 2. Bot Changes (polystrike-bot)

**File: `bot.py`**
- Modified `execute_signal()` to use `token_id` from signal directly
- Removed `get_token_id_for_bucket()` stub method (no longer needed)
- Updated `check_stop_losses()` to fetch token_id from current signals
- Added configuration validation on startup

**File: `polymarket_client.py`**
- Added missing `Dict` import from typing
- Implemented `get_balance()` using py-clob-client

**File: `config.py`**
- Added `validate_config()` function with comprehensive validation rules
- Validates API keys, wallet credentials, and trading parameters

## How It Works

### Signal Flow with token_id

```
1. Gamma API → polymarket_fetcher.py
   - Fetches market data including clobTokenIds

2. Database → elon_market_snapshots
   - Stores: event_id, market_title, token_id, yes_price, volume

3. Prediction Worker → signal_generator.py
   - Reads market data with token_ids
   - Generates signals with token_id included

4. API Response → /signals/elon
   - Returns signals with token_id field

5. Bot → execute_signal()
   - Reads token_id from signal
   - Passes directly to Polymarket CLOB client
```

### Example Signal Response

```json
{
  "event_id": 236151,
  "bucket": "65-89",
  "token_id": "0x1234567890abcdef...",
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

## Deployment Steps

### Backend (Polystrike)

```bash
# 1. Run migration on production database
cd /Users/dizpers/projects/polystrike
python3 src/scripts/migrate_add_token_id.py /opt/polystrike/data/polystrike.db

# 2. Deploy backend changes
git add src/ingest/polymarket_fetcher.py
git add src/storage/sqlite_handler.py
git add src/services/signal_generator.py
git add src/scripts/migrate_add_token_id.py
git commit -m "Add token_id support to signals endpoint"
git push origin main

# 3. Deploy via Ansible
cd deploy/ansible
uv run ansible-playbook -i inventory.ini playbook.yml

# 4. Restart services
ssh linuxuser@45.63.41.191
sudo systemctl restart polystrike-polymarket
sudo systemctl restart polystrike-prediction
```

### Bot (polystrike-bot)

```bash
# 1. Setup environment
cd /Users/dizpers/projects/polystrike-bot
cp .env.example .env
# Edit .env with your credentials

# 2. Install dependencies
uv venv
source .venv/bin/activate
uv pip install -e .

# 3. Test in dry-run mode
DRY_RUN=true python3 bot.py
```

## Required API Keys

### Polystrike Pro API
- **Key**: `POLYSTRIKE_API_KEY=ps_pro_xxxxx`
- **Cost**: $79/month
- **Get it**: https://polystrike.xyz

### Polymarket Wallet
- **Private Key**: `WALLET_PRIVATE_KEY=0x...` (66 chars)
- **Address**: `WALLET_ADDRESS=0x...` (42 chars)
- **Network**: Polygon (Chain ID 137)

**Important**: For automated trading, you MUST have the wallet's private key. The bot needs to cryptographically sign each trade. Options:
1. Export from existing MetaMask wallet
2. Create dedicated trading wallet (recommended for security)
3. Use DRY_RUN=true for testing without private key

### Telegram Bot (Optional)
- **Token**: `TELEGRAM_BOT_TOKEN=...`
- **Chat ID**: `TELEGRAM_CHAT_ID=...`
- **Get it**: Message @BotFather on Telegram

## Verification

### 1. Verify Backend Changes

```bash
# Check if token_id column exists
ssh linuxuser@45.63.41.191
sqlite3 /opt/polystrike/data/polystrike.db "PRAGMA table_info(elon_market_snapshots);"
# Should show token_id column

# Check if token_ids are being captured
sqlite3 /opt/polystrike/data/polystrike.db \
  "SELECT market_title, token_id FROM elon_market_snapshots WHERE token_id IS NOT NULL LIMIT 5;"
```

### 2. Verify API Response

```bash
# Test signals endpoint
curl -H "X-API-Key: ps_pro_xxxxx" \
  "https://polystrike.xyz/api/v1/signals/elon?bankroll=100" | jq '.data[0].signals[0].token_id'
# Should return a token_id (not null)
```

### 3. Verify Bot

```bash
# Run in dry-run mode
cd /Users/dizpers/projects/polystrike-bot
DRY_RUN=true python3 bot.py

# Check logs for token_id
tail -f trades.log | grep "Token ID"
```

## What's Still Needed

### Testing Infrastructure
- Unit tests for risk_manager
- Integration tests for bot
- Mock fixtures for API responses
- Historical event replay tests

See the plan file for detailed test implementation: `/Users/dizpers/.claude/plans/scalable-napping-oasis.md`

### Next Steps
1. Run backend migration and deploy
2. Verify token_ids are being captured
3. Test bot in dry-run mode
4. Create test infrastructure
5. Test with small amounts in live mode

## Troubleshooting

### "No token_id provided for bucket"
- **Cause**: Backend hasn't captured token_ids yet
- **Fix**: Wait for next market price fetch cycle (1 minute) or restart polystrike-polymarket service

### "WALLET_PRIVATE_KEY is required"
- **Cause**: Missing private key in .env
- **Fix**: Set DRY_RUN=true for testing, or add private key for live trading

### "POLYSTRIKE_API_KEY must start with 'ps_pro_'"
- **Cause**: Using wrong API key tier
- **Fix**: Get Pro API key from https://polystrike.xyz

## Security Notes

- Never commit .env file (already in .gitignore)
- Use dedicated wallet with limited funds for bot trading
- Start with small amounts ($100-500)
- Keep private key encrypted at rest if possible
- Monitor trades closely in first 24-48 hours
