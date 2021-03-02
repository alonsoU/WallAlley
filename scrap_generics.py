from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import numpy as np


def google_search(text_search):
    with webdriver.Chrome("C:/Users/Alonso Uribe/AppData/Local/Chromium/User Data/chromedriver.exe") as driver:
        driver.get("https://www.google.com/")
        text_box = driver.find_element(By.XPATH, "//input[@class='gLFyf gsfi']")
        webdriver.ActionChains(driver)\
            .move_to_element(text_box)\
            .send_keys(text_search, Keys.ENTER)\
            .perform()
        url_search = driver.current_url
        return url_search

search = "Arriendo Casa Santiago 3 dormitorios"
#url = google_search(search)
def find_pages(text_search):
    #searching_url = google_search(text_search)
    with webdriver.Chrome("C:/Users/Alonso Uribe/AppData/Local/Chromium/User Data/chromedriver.exe") as driver:
        driver.get("https://www.google.com/")
        text_box = driver.find_element(By.XPATH, "//input[@class='gLFyf gsfi']")
        webdriver.ActionChains(driver) \
            .move_to_element(text_box) \
            .send_keys(text_search, Keys.ENTER) \
            .perform()
        content = driver.page_source
        soup = BeautifulSoup(content, 'html.parser')
    url_list = []
    for url_section in soup.findAll('div', attrs={'class':'g'}):
        a = url_section.find("a", href=True)
        url_list.append(a["href"])

    url_set = {url for url in url_list}
    print(url_set)
    return url_set

find_pages(search)



