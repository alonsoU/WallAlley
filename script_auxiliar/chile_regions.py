from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import numpy as np

rows = []
with webdriver.Chrome("C:/Users/Alonso Uribe/AppData/Local/Chromium/User Data/chromedriver.exe") as driver:
        driver.get("https://es.wikipedia.org/wiki/Anexo:Comunas_de_Chile")
        content = driver.page_source
        soup = BeautifulSoup(content, 'html.parser')
table_content = soup.find('table', class_="wikitable sortable jquery-tablesorter")
table_labels = table_content.find('thead')
table_labels = [th.text for th in table_labels.find_all('th')]
table_body = table_content.find('tbody')
rows = []
for row in table_body.find_all('tr'):
    values = [value.text for value in row.find_all('td')]
    rows.append(values)

#############
# Pre-process
#############

df = pd.DataFrame(rows)
df = df.drop(columns=9)
table_labels[0] = "CUT"
table_labels[1] = "Comuna"
table_labels = [label.strip("\n").lower() for label in table_labels]
df.columns = table_labels
df = df.applymap(lambda x: x.strip("\n").strip().lower())
df[table_labels[5]] = df[table_labels[5]].apply(lambda x: x.replace(".", "").replace(",", "."))
df[table_labels[6]] = df[table_labels[6]].apply(lambda x: x.replace(".", ""))
df[table_labels[7]] = df[table_labels[7]].apply(lambda x: x.replace(",", "."))
df = df.applymap(lambda x: (float(x)) if x.isnumeric() else x)
df = df.convert_dtypes()
print(df.head(10))
for column in df:
    print(df[column].dtype)

df.to_csv('../data/communes_of_chile.csv', index=False)