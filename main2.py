from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import requests

bot_token= '7731248996:AAFKGHP-xBCYt1BxlcOLYFnk7FaziSUN9J4'
chat_id= '1113954519'

# url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
# requests.get(url).json()

def web_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--verbose")
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument("--window-size=1920, 1200")
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    return driver

driver = web_driver()
driver.get("https://www.investorgain.com/report/live-ipo-gmp/331/current/")

body = driver.find_element(By.TAG_NAME, "body")

soup = BeautifulSoup( body.get_attribute("outerHTML") , "html.parser")
table = soup.find("table", class_= "report-main-table w-auto table table-striped table-bordered table-hover" )  # soup.find("table")  # Adjust the tag if necessary
print("body:", body, " soup :")
print(len(soup.find_all("table")))


print("tables: " ,soup.find_all("table"))

if not table: print("Table not found in the element.")
    # Extract headers
headers = [th.text.strip() for th in table.find_all("th")]

# Extract rows
rows = []
for row in table.find_all("tr")[1:]:  # Skip the header row
    rows.append([td.text.strip() for td in row.find_all("td")])

# Create the DataFrame
df = pd.DataFrame(rows, columns=headers)


message= f"{len(df)}"

url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}"
req= requests.get(url).json()
