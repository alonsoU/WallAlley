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
        wait = WebDriverWait(driver, 10)
        cookies = driver.find_element(By.XPATH, "//button[@id='cookieDisclaimerButton']")
        try:
            webdriver.ActionChains(driver).click(cookies).perform()
        except NoSuchElementException:
            pass
        driver.implicitly_wait(1)
        curr_url = driver.current_url
        driver.find_element(By.XPATH, "//searchbox-button[@id='search-submit']").click()
        wait.until(EC.url_changes(curr_url))
        # All this identation code belongs to the scrapping of one configuration of higher
        # variable through all pages displayed to the corresponing variables.
        max_iter = 100
        for sell_type in :
                for property_type in :
        for i in range(max_iter):
                # This is the scrapping of just one page of the higher variables's configuration
                print(f"Scrapping page {i + 1}")
                content = driver.page_source
                soup = BeautifulSoup(content, "html.parser")
                for house in soup.findAll("li", class_="ui-search-layout__item"):
                        price_elem = house.find("span")
                        price = [price_elem.text]
                        features_elems = house.findAll("li")
                        features = [elem.text for elem in features_elems]
                        location_elem = house.findAll("p")
                        location = [elem.text for elem in location_elem]
                        all = [item.strip().lower() for sublist in [price, features, location] for item in sublist]
                        rows.append(all)
                next_page_locator = By.XPATH, "//a[@title='Siguiente' and @role='button']"
                try:
                        next_page = driver.find_element(*next_page_locator)  # Two elements with the same class, Previous and Next
                        # location = {'x': 684, 'y': 10815}
                        next_url = next_page.get_attribute("href")
                except NoSuchElementException:
                        print("All pages seen")
                        break
                wait.until(EC.element_to_be_clickable(next_page_locator))
                webdriver.ActionChains(driver) \
                        .move_to_element(next_page) \
                        .click(next_page).perform()
                wait.until(EC.url_to_be(next_url))  # Waiting until it's at the url clicked
                wait.until(EC.visibility_of_all_elements_located(
                        (By.XPATH, "//li[@class='ui-search-layout__item']")))  # until all list elements can be seen



