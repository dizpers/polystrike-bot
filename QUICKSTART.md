# Polystrike Bot - Quick Start

## ✅ Setup Complete

Your bot is installed and tested locally. All 16 tests passing.

## 🔑 Required: Configure API Key

Edit `.env` and add your Polystrike Pro API key:

```bash
# Open .env in your editor
nano .env

# Update this line:
POLYSTRIKE_API_KEY=ps_pro_your_actual_key_here
```

Get your API key from: https://polystrike.xyz

## 🧪 Test the Bot (Dry-Run)

```bash
cd /Users/dizpers/projects/polystrike-bot
source .venv/bin/activate
python3 bot.py
```

This will:
- Fetch real signals from Polystrike API
- Show what trades it would make
- NOT execute any real trades (DRY_RUN=true by default)

## 📊 What You'll See

```
🚀 Polystrike Trading Bot started
Bankroll: $100.00
Max position: $30.00
Min edge: 5.0%
Poll interval: 300s

🔍 Fetching signals from Polystrike API...
📊 Current exposure: 0.0% of bankroll

💰 Found 2 BUY signal(s)
============================================================
💰 BUY Signal: Event 236151 → 65-89
   Token ID: 0xabc123...
   Model: 72% vs Market: 45%
   Edge: +27.0% | EV: $+0.600/$
   Kelly: 15.0% | Bet: $15.00
   Confidence: HIGH
============================================================

🔧 DRY RUN: Would buy $15.00 of 65-89
```

## 🚀 Deploy Backend (Required for Live Trading)

Before going live, deploy backend changes to add token_id support:

```bash
cd /Users/dizpers/projects/polystrike

# 1. SSH and run migration
ssh -i ~/.ssh/polystrike linuxuser@45.63.41.191 \
  "cd /opt/polystrike/current && python3 src/scripts/migrate_add_token_id.py /opt/polystrike/data/polystrike.db"

# 2. Deploy via Ansible
cd deploy/ansible
uv run ansible-playbook -i inventory.ini playbook.yml

# 3. Verify (wait 1-2 min for market refresh)
curl -H "X-API-Key: YOUR_KEY" \
  "https://polystrike.xyz/api/v1/signals/elon?bankroll=100" | \
  jq '.data[0].signals[0].token_id'
```

## 💰 Go Live (After Testing)

1. Export private key from MetaMask
2. Update `.env`:
   ```bash
   WALLET_PRIVATE_KEY=0x...
   WALLET_ADDRESS=0x...
   DRY_RUN=false
   ```
3. Start with small bankroll:
   ```bash
   BANKROLL=100 python3 bot.py
   ```

## 📚 Documentation

- `README.md` - Overview and features
- `DEPLOYMENT_CHECKLIST.md` - Detailed deployment steps
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `verify_setup.py` - Automated verification

## 🆘 Troubleshooting

**"401 Unauthorized"**
- Add your real Polystrike Pro API key to `.env`

**"No token_id in signals"**
- Deploy backend changes first
- Wait 1-2 minutes for market prices to refresh

**"WALLET_PRIVATE_KEY is required"**
- Set `DRY_RUN=true` for testing without wallet
- Or add private key from MetaMask for live trading
