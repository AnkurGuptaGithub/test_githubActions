
# url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
# requests.get(url).json()

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('CHAT_ID') 

def extract_ipo_data():
    url = "https://ipowatch.in/ipo-grey-market-premium-latest-ipo-gmp/"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes

    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("figure", class_="wp-block-table")

    if not table:
        print("Table not found on the page.")
        return None

    headers = [header.text.strip() for header in table.find_all("tr")[0].find_all("td")]
    rows = []
    for row in table.find_all("tr")[1:]:  # Skip the header row
        rows.append([cell.text.strip() for cell in row.find_all("td")])

    df = pd.DataFrame(rows, columns=headers)
    return df

ipo_data = extract_ipo_data()

ipo_data = ipo_data.replace("-%", "0%")
ipo_data['Gain_value'] = ipo_data['Gain'].apply(lambda x: float(x.replace('%','')))

Mainboard = ipo_data[ipo_data.Type=="Mainboard"][ipo_data.Gain_value>10].sort_values(by='Gain_value', ascending=False).reset_index(drop=True)
SME = ipo_data[ipo_data.Type!="Mainboard"][ipo_data.Gain_value>10].sort_values(by='Gain_value', ascending=False).reset_index(drop=True)

message=""

if not SME.empty: message+= "SME \n"

for i in range(len(SME)):
  message +=   "{}".format(SME["Current IPOs"][i]) + " @" + "{}".format(SME["Gain"][i]) + "\n"

if not Mainboard.empty: message+= "Mainboard \n"

for i in range(len(Mainboard)):
  message +=   "{}".format(SME["Current IPOs"][i]) + " @" + "{}".format(SME["Gain"][i]) + "\n"

url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}"
req= requests.get(url).json()

