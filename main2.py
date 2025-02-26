from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
from datetime import datetime
from datetime import date

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
time.sleep(10)

body = driver.find_element(By.TAG_NAME, "body")

soup = BeautifulSoup( body.get_attribute("outerHTML") , "html.parser")
table = soup.find("table", class_= "report-main-table w-auto table table-striped table-bordered table-hover" )  # soup.find("table")  # Adjust the tag if necessary

if not table: 
  print("Table not found in the element.")
  exit()
    # Extract headers
headers = [th.text.strip() for th in table.find_all("th")]

# Extract rows
rows = []
for row in table.find_all("tr")[1:]:  # Skip the header row
    rows.append([td.text.strip() for td in row.find_all("td")])

# Create the DataFrame
df = pd.DataFrame(rows, columns=headers)

if len(df)<1:
  message= "Table not found in the element."
  exit()
else: message= ''
  
df.columns = df.columns.str.replace(' ', '')
df.GMP = df.GMP.str.replace('--','0').astype('float')
df.Price = df.Price.str.replace('--','0').astype('float')
df['Close'] = df['Close'].apply(convert_date)
df['BoADt'] = df['BoADt'].apply(convert_date)
df['Listing'] = df['Listing'].apply(convert_date)

try:
  apply = pd.read_csv('apply.csv')
except:
  apply = pd.DataFrame(columns= df.columns)

listings = df[ df.Listing==date.today() ][ df.IPO.isin(apply.IPO) ].reset_index(drop=True)

if not listings.empty: message+= "Listings \n"
for i in range(len(listings)):
  message +=   "{}".format(listings["IPO"][i]) + " @" + "{}".format(listings["EstListing"][i]) + "\n"

allots = df[df.BoADt==date.today()][df.IPO.isin(apply.IPO)].reset_index(drop=True)

if not allots.empty: message+= "Allotment \n"
for i in range(len(allots)):
  message +=   "{}".format(allots["IPO"][i]) + " @" + "{}".format(allots["EstListing"][i]) + "\n"

df = df.join(apply.set_index('IPO'), on='IPO', rsuffix='_apply').reset_index(drop=True)

newIPO = df[ df.Status.str.contains('Open') ][ ~df.IPO.isin(apply.IPO) ][ (df.IPO.str.contains('IPO') & (df.GMP/df.Price>0.2)) | 
 (df.IPO.str.contains('SME') & (df.GMP/df.Price>0.3)) | 
  (df.FireRating.str.count('🔥') >2)].reset_index(drop=True)

if not newIPO.empty: message+= "New IPOs \n"
for i in range(len(newIPO)):
  message +=   "{}".format(newIPO["IPO"][i]) + " @" + "{}".format(newIPO["EstListing"][i]) + "\n"

trending = df[ df.Status.str.contains('Open') ][df.IPO.isin(apply.IPO)][(((df.GMP-df.GMP_apply.astype(float))/df.Price)>0.1 ) | 
  (df.FireRating.str.count('🔥') >2) ].reset_index(drop=True)

if not trending.empty: message+= "Trending \n"
for i in range(len(trending)):
  message +=   "{}".format(trending["IPO"][i]) + " @" + "{}".format(trending["EstListing"][i]) + "\n"

apply = apply[ ~apply.IPO.isin( df[df.IPO.isin(apply.IPO)][((df.GMP_apply.astype(float) - df.GMP)/df.Price)>0.1 ].IPO )].reset_index(drop=True)

apply = pd.concat([apply, newIPO], ignore_index=True).reset_index(drop=True)

apply.to_csv('apply.csv')

url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}"
req= requests.get(url).json()
