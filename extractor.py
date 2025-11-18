"""Helpers for extracting direct links from Terabox.
This uses a third-party API endpoint (example). Replace with a more reliable extractor if needed.
"""
import requests




TERA_API = 'https://teradownloader.com/api/getdownload'




def extract_direct_link(share_url: str) -> str | None:
try:
res = requests.post(TERA_API, data={'url': share_url}, timeout=30)
res.raise_for_status()
data = res.json()
# expected JSON: {"download": "https://..."}
if isinstance(data, dict) and data.get('download'):
return data['download']
except Exception:
return None
return None
