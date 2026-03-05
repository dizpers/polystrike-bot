# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-06

### Added
- Initial release of Polystrike Trading Bot
- Automated signal polling from Polystrike API
- Risk management with Kelly Criterion position sizing
- Smart stop-loss with model probability override
- Polymarket CLOB integration via py-clob-client
- Dry-run mode for testing without real trades
- Manual approval mode for cautious traders
- Comprehensive configuration via .env file
- Position monitoring script
- Telegram alerts support (optional)
- Trading rules enforcement from Polystrike memory
- Detailed logging to trades.log

### Known Limitations
- Token ID mapping not yet implemented (requires Polystrike API enhancement)
- Telegram alerts not fully implemented
- No backtesting framework yet
- Single-event focus (Elon tweets only)

### Documentation
- Comprehensive README with setup instructions
- Troubleshooting guide
- Contributing guidelines
- Marketing analysis
- MIT License

## [Unreleased]

### Planned Features
- Token ID mapping via Polystrike API
- Multi-event support (crypto, weather markets)
- Backtesting framework
- Web dashboard for monitoring
- Advanced order types (limit orders, stop-limit)
- Portfolio rebalancing logic
- Performance analytics
