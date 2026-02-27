# KabaevBotTg

Run the bot directly from a Python virtual environment (`venv`), without Docker.

## 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Configure environment

```bash
cp .env.example .env
```

Set at least:
- `TG_BOT_TOKEN`
- `ADMIN_TG_ID`
- `DATABASE_URL`

If DB access is over SSH tunnel, set `SSH_TUNNEL_ENABLED=1` and related `SSH_*` variables.

## 3. Start bot

```bash
python main.py
```

The bot now includes:
- polling reconnect backoff for Telegram API network failures;
- process-level auto-restart loop with exponential backoff if polling exits/crashes.

## 4. Optional: run as systemd service (Linux)

Create `/etc/systemd/system/kabaevbot.service`:

```ini
[Unit]
Description=Kabaev Telegram Bot
After=network.target

[Service]
Type=simple
User=apbot
WorkingDirectory=/home/apbot/KabaevBotTg
ExecStart=/home/apbot/KabaevBotTg/.venv/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now kabaevbot
sudo systemctl status kabaevbot
```
