
# url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
# requests.get(url).json()

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('CHAT_ID') 

with open('check_file.txt', 'r') as f:
    content = f.read()

if int(content) != 7 :
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={"Test failed"}"
    req= requests.get(url).json()

with open('check_file.txt', 'w') as f:
    f.write(0)

