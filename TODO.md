# TODO

## Critical (Before Public Launch)

- [ ] **Token ID Mapping**: Implement `get_token_id_for_bucket()` function
  - Option 1: Add `/markets/elon` endpoint to Polystrike API
  - Option 2: Use Polymarket's market discovery API
  - Option 3: Maintain local cache of event_id -> token_id mappings

- [ ] **Test with Real Wallet**: Verify Polymarket integration works end-to-end
  - Test market buy orders
  - Test market sell orders
  - Verify allowances are set correctly

- [ ] **Telegram Alerts**: Implement notification system
  - Trade execution alerts
  - Stop-loss triggers
  - Daily P&L summary

## High Priority

- [ ] **Portfolio Sync**: Fetch existing positions on startup
  - Avoid duplicate entries
  - Resume monitoring existing positions

- [ ] **Better Error Handling**: Graceful degradation
  - API timeout handling
  - Network error recovery
  - Invalid signal handling

- [ ] **Position Database**: Track trade history locally
  - SQLite database for trades
  - P&L calculation
  - Performance analytics

## Medium Priority

- [ ] **Backtesting Framework**: Test strategies on historical data
  - Load historical signals from Polystrike
  - Simulate trades
  - Calculate Sharpe ratio, max drawdown

- [ ] **Web Dashboard**: Simple Flask/FastAPI UI
  - Real-time position monitoring
  - Trade history
  - Performance charts

- [ ] **Multi-Event Support**: Trade crypto and weather markets
  - Generalize signal handling
  - Event-specific risk parameters

## Low Priority

- [ ] **Advanced Order Types**: Limit orders, stop-limit
- [ ] **Portfolio Rebalancing**: Automatically adjust positions
- [ ] **Paper Trading Mode**: Simulate trades without API calls
- [ ] **Docker Support**: Containerize the bot
- [ ] **Systemd Service**: Run as background service

## Documentation

- [ ] **Video Tutorial**: YouTube walkthrough
- [ ] **Blog Post**: "How I Built a Profitable Trading Bot"
- [ ] **API Integration Guide**: For Polystrike API users
- [ ] **Risk Management Deep Dive**: Explain Kelly Criterion

## Community

- [ ] **Discord Channel**: Create #bot-users channel
- [ ] **Example Strategies**: Share profitable configurations
- [ ] **User Success Stories**: Feature testimonials
- [ ] **FAQ**: Common questions and answers
