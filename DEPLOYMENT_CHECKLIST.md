# Deployment Checklist

## ✅ Completed

### Backend (Polystrike)
- [x] Modified `polymarket_fetcher.py` to extract `clobTokenIds` from Gamma API
- [x] Added `token_id` column to `elon_market_snapshots` table schema
- [x] Updated `signal_generator.py` to include `token_id` in Signal dataclass
- [x] Created migration script `migrate_add_token_id.py`
- [x] Committed changes (commit: d873974)

### Bot (polystrike-bot)
- [x] Updated `bot.py` to use `token_id` from signals
- [x] Removed `get_token_id_for_bucket()` stub
- [x] Fixed `check_stop_losses()` to fetch token_id from signals
- [x] Added configuration validation to `config.py`
- [x] Fixed `polymarket_client.py` imports and balance checking
- [x] Created test infrastructure (pytest, conftest, test files)
- [x] Created documentation (README, IMPLEMENTATION_SUMMARY, README_SETUP)
- [x] Created `verify_setup.py` script

## 🚀 Ready to Deploy

### Step 1: Deploy Backend Changes

```bash
cd /Users/dizpers/projects/polystrike

# 1. Push to GitHub
git push origin main

# 2. SSH to production server
ssh -i ~/.ssh/polystrike linuxuser@45.63.41.191

# 3. Run migration
cd /opt/polystrike/current
python3 src/scripts/migrate_add_token_id.py /opt/polystrike/data/polystrike.db

# 4. Exit SSH
exit

# 5. Deploy via Ansible
cd deploy/ansible
uv run ansible-playbook -i inventory.ini playbook.yml

# 6. Verify services restarted
ssh -i ~/.ssh/polystrike linuxuser@45.63.41.191 \
  "sudo systemctl status polystrike-polymarket polystrike-prediction --no-pager"
```

### Step 2: Verify Backend Deployment

```bash
# Wait 1-2 minutes for market prices to refresh, then check:
curl -H "X-API-Key: YOUR_PRO_KEY" \
  "https://polystrike.xyz/api/v1/signals/elon?bankroll=100" | \
  jq '.data[0].signals[0] | {bucket, token_id, action}'

# Should show token_id (not null)
```

### Step 3: Setup Bot

```bash
cd /Users/dizpers/projects/polystrike-bot

# 1. Install dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[test]"

# 2. Configure
cp .env.example .env
# Edit .env with your credentials:
#   POLYSTRIKE_API_KEY=ps_pro_xxxxx
#   WALLET_PRIVATE_KEY=0x... (for live trading)
#   WALLET_ADDRESS=0x...
#   DRY_RUN=true (for testing)

# 3. Verify setup
python3 verify_setup.py

# 4. Run tests
pytest -v
```

### Step 4: Test Bot

```bash
# Test in dry-run mode (no real trades)
DRY_RUN=true python3 bot.py

# Watch logs in another terminal
tail -f trades.log

# Should see:
# - Configuration validated
# - Fetching signals
# - Token IDs in signal logs
# - DRY RUN messages for trades
```

### Step 5: Go Live (Optional)

```bash
# Only after successful dry-run testing!

# 1. Get wallet private key from MetaMask
# 2. Update .env with real credentials
# 3. Set DRY_RUN=false
# 4. Start with small bankroll

BANKROLL=100 python3 bot.py
```

## 📋 Pre-Flight Checklist

Before going live, verify:

- [ ] Backend deployed and token_ids appearing in signals
- [ ] Bot tests passing (`pytest`)
- [ ] Dry-run mode tested for 1+ hour
- [ ] Polystrike Pro API key valid
- [ ] Wallet has USDC on Polygon
- [ ] Telegram alerts configured (optional)
- [ ] Risk limits appropriate for bankroll
- [ ] Monitoring plan in place

## 🔍 Verification Commands

```bash
# Check backend token_ids
curl -H "X-API-Key: YOUR_KEY" \
  "https://polystrike.xyz/api/v1/signals/elon?bankroll=100" | \
  jq '.data[0].signals[] | select(.action=="BUY") | {bucket, token_id}'

# Check bot config
cd /Users/dizpers/projects/polystrike-bot
python3 verify_setup.py

# Run tests
pytest -v

# Check positions
python3 check_positions.py
```

## 📊 Success Criteria

- ✅ Backend: `/signals/elon` returns `token_id` for each signal
- ✅ Bot: Can fetch signals and extract token_id
- ✅ Bot: Dry-run mode shows "Would buy" messages with token_id
- ✅ Tests: All pytest tests passing
- ✅ Config: Validation catches errors

## 🆘 Troubleshooting

### "No token_id in signals"
- Wait 1-2 minutes after deployment for market prices to refresh
- Check `polystrike-polymarket` service is running
- Verify migration ran successfully

### "WALLET_PRIVATE_KEY is required"
- Set `DRY_RUN=true` for testing without wallet
- Or add private key from MetaMask for live trading

### "API key must start with ps_pro_"
- Get Pro API key from https://polystrike.xyz
- Free tier doesn't have access to `/signals` endpoint

## 📚 Documentation

- `README.md` - Quick start guide
- `README_SETUP.md` - Detailed setup instructions
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `verify_setup.py` - Automated verification script
- `/Users/dizpers/.claude/plans/scalable-napping-oasis.md` - Full implementation plan

## 🎯 Next Steps

1. Deploy backend changes (Step 1)
2. Verify token_ids in API (Step 2)
3. Setup and test bot (Steps 3-4)
4. Monitor in dry-run for 24h
5. Go live with small amounts (Step 5)

---

**Status**: ✅ Implementation complete, ready for deployment
**Estimated deployment time**: 15-20 minutes
**Testing time**: 1-2 hours dry-run recommended
