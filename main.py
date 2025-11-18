#!/usr/bin/env python3
"""Terabox Pyrogram Userbot
Usage:
 - /tb <terabox_link>   # starts download -> upload

Environment variables (or .env):
 - API_ID
 - API_HASH
 - SESSION_NAME  (Pyrogram session name or path to session file)
 - ADMINS  (comma-separated Telegram user IDs allowed to use commands)

"""
import os
import asyncio
import shlex
import subprocess
import logging
from pathlib import Path
from dotenv import load_dotenv
from pyrogram import Client, filters
from extractor import extract_direct_link

load_dotenv()

API_ID = int(os.getenv('API_ID', '0'))
API_HASH = os.getenv('API_HASH', '')
SESSION_NAME = os.getenv('SESSION_NAME', 'terabox_session')
ADMINS = [int(x) for x in os.getenv('ADMINS','').split(',') if x.strip().isdigit()]

# Where downloads live temporarily
TMP_DIR = Path(os.getenv('TMP_DIR','./tmp'))
TMP_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name)

app = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH, workdir='.')


async def aria2_download(url: str, output_path: Path):
    """Download using aria2c with multiple connections."""
    cmd = [
        'aria2c',
        '--continue=true',
        '-x', '16',
        '-s', '16',
        '-k', '1M',
        '-d', str(output_path.parent),
        '-o', str(output_path.name),
        url
    ]
    logger.info('Running: %s', ' '.join(shlex.quote(p) for p in cmd))
    proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    out, err = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f'aria2c failed: {err.decode(errors="ignore")}')
    return output_path


@app.on_message(filters.command('tb') & filters.private)
async def tb_handler(client, message):
    try:
        sender = message.from_user.id if message.from_user else None
        if ADMINS and sender not in ADMINS:
            return await message.reply_text('⚠️ You are not authorized to use this bot.')

        if len(message.command) < 2:
            return await message.reply_text('Usage: /tb <terabox_link>')

        share_url = message.command[1]
        status = await message.reply_text('🔍 Extracting direct link...')

        direct = extract_direct_link(share_url)
        if not direct:
            return await status.edit('❌ Could not extract a direct link.')

        await status.edit('📥 Starting download...')
        # derive filename
        fname = direct.split('/')[-1].split('?')[0] or 'download.bin'
        out_path = TMP_DIR / fname

        await aria2_download(direct, out_path)
        await status.edit(f'✅ Download finished: {out_path.name}\n📤 Uploading...')

        # Upload with pyrogram (user account allows large files)
        await client.send_document(chat_id=message.chat.id, document=str(out_path), caption=f'Uploaded: {out_path.name}')
        await status.edit('✅ Upload complete!')

        try:
            out_path.unlink()
        except Exception:
            pass

    except Exception as e:
        await message.reply_text(f'Error: {e}')
