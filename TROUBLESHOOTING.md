# Troubleshooting Guide

## Common Issues

### "Invalid API Key"

**Problem**: Bot fails with authentication error.

**Solution**:
1. Check that your API key starts with `ps_pro_`
2. Verify the key is active at https://polystrike.xyz/account
3. Ensure no extra spaces in `.env` file

### "No signals found"

**Problem**: Bot runs but never finds BUY signals.

**Possible Causes**:
1. **No opportunities**: Market is fairly priced, no edge available
2. **Risk filters**: Your `MIN_EDGE` or `MIN_CONFIDENCE` is too strict
3. **Timing**: Signals are most frequent in final 24 hours of events

**Solution**:
- Lower `MIN_EDGE` to 0.03 (3%)
- Set `MIN_CONFIDENCE=LOW`
- Check `/api/v1/signals/elon` manually to see raw signals

### "Insufficient balance"

**Problem**: Polymarket order fails with insufficient USDC.

**Solution**:
1. Check your wallet balance on Polymarket
2. Ensure `BANKROLL` in `.env` matches your actual balance
3. Lower `MAX_POSITION_SIZE` if needed

### "Token allowance not set"

**Problem**: First trade fails with allowance error.

**Solution**:
You need to approve USDC and Conditional Token contracts:
```python
# Run this once before trading
from polymarket_client import PolymarketClient
client = PolymarketClient(private_key="0x...", chain_id=137)
client.client.set_allowances()  # Approve contracts
```

### Bot stops after one cycle

**Problem**: Bot exits instead of running continuously.

**Solution**:
- Check for Python errors in `trades.log`
- Ensure `POLL_INTERVAL_SECONDS` is set
- Run with `python -u bot.py` to see unbuffered output

### "Model probability below 50%"

**Problem**: All signals are skipped with this message.

**Explanation**: This is a safety rule (Rule #10 from Polystrike memory). The bot only trades when the model is confident (>50% probability).

**Solution**: This is working as intended. Wait for higher-confidence signals.

### Dry run mode not working

**Problem**: Real trades execute even with `DRY_RUN=true`.

**Solution**:
- Check `.env` file has `DRY_RUN=true` (not `True` or `1`)
- Restart the bot after changing `.env`
- Look for "🔧 DRY RUN MODE" in logs at startup

## Getting Help

If you're still stuck:
1. Check `trades.log` for detailed error messages
2. Open an issue on GitHub with logs (remove API keys!)
3. Join our Discord for community support

## Performance Issues

### Bot is slow

**Possible Causes**:
- Network latency to Polystrike API
- Polymarket RPC node is slow

**Solution**:
- Increase `POLL_INTERVAL_SECONDS` to 600 (10 minutes)
- Use a faster RPC endpoint (Alchemy, Infura)

### High gas fees

**Problem**: Polygon gas fees are unexpectedly high.

**Solution**:
- Wait for lower network congestion
- Batch trades if possible
- Consider if trade size justifies gas cost

## Safety Checks

Before running with real money:

- [ ] Test in `DRY_RUN=true` mode for 24 hours
- [ ] Verify stop-loss triggers correctly
- [ ] Check position size limits work
- [ ] Confirm Telegram alerts arrive (if configured)
- [ ] Start with small `BANKROLL` ($50-100)
- [ ] Monitor first few trades closely

## Emergency Stop

To immediately stop the bot:
1. Press `Ctrl+C` in the terminal
2. Or: `kill $(pgrep -f bot.py)`

The bot will finish the current cycle and exit gracefully.
