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
        driver.get("https://www.portalinmobiliario.com/")
        cookies = driver.find_element(By.XPATH, "//button[@id='cookieDisclaimerButton']")
        try:
            webdriver.ActionChains(driver).click(cookies).perform()
        except NoSuchElementException:
            pass
        driver.implicitly_wait(2)
