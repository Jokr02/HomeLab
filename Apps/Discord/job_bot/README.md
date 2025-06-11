# 💼 Discord Job Bot

A fully automated Discord bot that sends you daily job postings from multiple platforms – including company ratings from Kununu – directly to your selected channel.

---

## ✨ Features

- 🔍 Job search from:
  - [Adzuna](https://adzuna.de)
  - [Joblift](https://joblift.de)
  - [Honeypot.io](https://www.honeypot.io)
  - [IHK job boards](https://www.dihk.de)
- ⭐ Employer reviews from [Kununu](https://kununu.com)
- 💬 Interactive "Save" and "Skip" buttons
- 💾 Favorite jobs saved per user
- 📅 Scheduled search every day at a configurable time
- ⚙️ Slash commands for configuration and favorite management
- 📈 Logging and log rotation
- 🌐 Easily customizable location, keywords, and distance

---

## 🧪 Requirements

- Python 3.9+
- Virtual environment (recommended)
- API credentials:
  - Discord Bot Token
  - Adzuna App ID + Key
  - (Optional) Joblift API Key

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/discord-jobbot.git
cd discord-jobbot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Create a .env file:

env
Kopieren
Bearbeiten
DISCORD_BOT_TOKEN=your_discord_token
DISCORD_CHANNEL_ID=your_channel_id
ADZUNA_APP_ID=your_adzuna_id
ADZUNA_APP_KEY=your_adzuna_key
ADZUNA_COUNTRY=de
JOBLIFT_API_KEY=your_joblift_api_key (optional)
ERROR_WEBHOOK_URL=https://discord.com/api/webhooks/... (optional)
⚙️ Configuration
The config is stored in config.json:

json
Kopieren
Bearbeiten
{
  "location": "Coburg",
  "radius": 100,
  "keywords": ["system administrator", "linux", "vmware"],
  "work_type": "all",
  "execution_time": "12:00"
}
You can also update it with /set_time or /config inside Discord.

✅ Commands
Command	Description
/favorites	Show your saved jobs
/clear_favorites	Clear your saved jobs
/set_time	Change the daily search time
/config	Show current job search configuration

🛠️ Autostart with systemd (optional)
ini
Kopieren
Bearbeiten
[Unit]
Description=Discord Job Bot
After=network.target

[Service]
ExecStart=/path/to/venv/bin/python /path/to/bot.py
WorkingDirectory=/path/to/discord-jobbot
Restart=always
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
Then:

bash
Kopieren
Bearbeiten
sudo systemctl daemon-reexec
sudo systemctl enable discord-jobbot
sudo systemctl start discord-jobbot
📋 License
MIT – feel free to use, modify, and contribute!

yaml
Kopieren
Bearbeiten

---

Wenn du möchtest, kann ich auch gleich eine `requirements.txt`, `.env.template` und Beispiel-`config.json` generieren. Sag einfach Bescheid!






