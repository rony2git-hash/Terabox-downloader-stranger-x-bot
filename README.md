# Terabox Pyrogram Userbot


This project runs a Pyrogram userbot that downloads files from Terabox share links and uploads them to Telegram (supports large uploads via a logged-in user account).


## Quick start
1. Copy `.env.example` to `.env` and fill in `API_ID`, `API_HASH`, `SESSION_NAME` (and optional `ADMINS` list).
2. Install requirements:
```bash
pip install -r requirements.txt
sudo apt-get update && sudo apt-get install -y aria2
