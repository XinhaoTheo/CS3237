import requests

TELEGRAM_API_TOKEN = "7710579435:AAF0lWMbc1UAWMIlrpNZxwVZeVyFsBC3a_4" 
TELEGRAM_CHAT_ID = "5430804464"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage"

def send_telegram_alert(message): 
    payload = { "chat_id": TELEGRAM_CHAT_ID, 
               "text": message } 
    try: 
        requests.post(TELEGRAM_API_URL, json=payload) 
    except Exception as e: 
        print(f"Failed to send Telegram message: {e}")