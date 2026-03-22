# Deployment Guide

This directory contains Ansible playbooks for deploying the Polystrike trading bot to a remote server.

## 🔐 Security First

**IMPORTANT:** Never commit secrets to git. The following files are gitignored:

- `ansible/inventory.ini` - Contains server IPs and SSH key paths
- `keys/` - Contains SSH deploy keys
- `.env.production` - Contains API keys and wallet credentials

## 📋 Prerequisites

1. **Ansible installed locally:**
   ```bash
   pip install ansible
   ```

2. **SSH access to your server:**
   - Ubuntu/Debian server with sudo access
   - SSH key authentication configured

3. **GitHub deploy key (optional):**
   - If repo is private, create a deploy key in GitHub settings
   - Save private key to `deploy/keys/github_deploy_key`

## 🚀 Quick Start

### 1. Setup Inventory

```bash
cd deploy/ansible
cp inventory.ini.example inventory.ini
nano inventory.ini
```

Update with your server details:
```ini
[bot]
192.168.1.100 ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/my_key
```

### 2. Create Production Environment File

```bash
cd /Users/dizpers/projects/polystrike-bot
cp .env .env.production
nano .env.production
```

Update with your production credentials:
```bash
POLYSTRIKE_API_KEY=ps_pro_your_real_key
WALLET_PRIVATE_KEY=0x...
WALLET_ADDRESS=0x...
DRY_RUN=false  # Set to false for live trading
```

### 3. Deploy

```bash
cd deploy/ansible
ansible-playbook playbook.yml
```

This will:
- Install system dependencies
- Clone the bot repository
- Install Python dependencies via uv
- Copy your .env.production file
- Install and start systemd service

## 📊 Managing the Bot

### Check Status
```bash
ssh user@your-server
sudo systemctl status polystrike-bot
```

### View Logs
```bash
ssh user@your-server
tail -f /opt/polystrike-bot/current/bot.log
tail -f /opt/polystrike-bot/current/trades.log
```

### Restart Bot
```bash
ssh user@your-server
sudo systemctl restart polystrike-bot
```

### Stop Bot
```bash
ssh user@your-server
sudo systemctl stop polystrike-bot
```

## 🔧 Manual Deployment (Alternative)

If you prefer not to use Ansible:

```bash
# SSH to server
ssh user@your-server

# Install dependencies
sudo apt update
sudo apt install -y git python3-venv python3-pip curl

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repo
git clone git@github.com:dizpers/polystrike-bot.git /opt/polystrike-bot
cd /opt/polystrike-bot

# Install dependencies
uv sync

# Create .env file
nano .env
# (paste your configuration)

# Run bot
uv run python bot.py
```

## 🔒 Security Best Practices

1. **Use a dedicated server user** (not root)
2. **Limit wallet funds** - Only keep what you're willing to trade
3. **Use firewall** - Only allow SSH (port 22)
4. **Monitor logs** - Set up alerts for errors
5. **Backup .env** - Store securely offline
6. **Rotate keys** - Change API keys periodically

## 🆘 Troubleshooting

### Bot won't start
```bash
# Check service status
sudo systemctl status polystrike-bot

# Check logs
journalctl -u polystrike-bot -n 50

# Verify .env file
cat /opt/polystrike-bot/current/.env
```

### "401 Unauthorized" errors
- Verify POLYSTRIKE_API_KEY in .env
- Ensure it starts with `ps_pro_`

### "No token_id in signals"
- Deploy backend changes first
- Wait 1-2 minutes for market prices to refresh

### Permission errors
```bash
# Fix ownership
sudo chown -R ubuntu:ubuntu /opt/polystrike-bot
```

## 📚 Additional Resources

- Main README: `../README.md`
- Quick Start: `../QUICKSTART.md`
- Deployment Checklist: `../DEPLOYMENT_CHECKLIST.md`
