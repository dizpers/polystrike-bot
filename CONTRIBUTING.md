# Contributing to Polystrike Bot

Thanks for your interest in contributing! This bot is designed to be a reference implementation for trading with Polystrike signals.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (Python version, OS)

### Suggesting Features

Feature requests are welcome! Please open an issue describing:
- The use case
- Why it would be valuable
- Proposed implementation (if you have ideas)

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly (especially with `DRY_RUN=true`)
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings for public functions
- Keep functions focused and small

### Testing

Before submitting a PR:
- Test in dry-run mode
- Verify no API keys are committed
- Check that all config options work
- Test error handling

## Development Setup

```bash
git clone https://github.com/polystrike/polystrike-bot.git
cd polystrike-bot
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Questions?

Open an issue or join our [Discord](https://discord.gg/polystrike).
