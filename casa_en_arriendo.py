from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import numpy as np

def scrap_pageone():
    rows = []
    with webdriver.Chrome("C:/Users/Alonso Uribe/AppData/Local/Chromium/User Data/chromedriver.exe") as driver:
        driver.get("https://www.portalinmobiliario.com/arriendo/casa/3-dormitorios/metropolitana#applied_filter"
                   "_id=state&applied_filte_name=Ubicaci%C3%B3n&applied_filter_order=1&applied_value_id="
                   "TUxDUE1FVEExM2JlYg&applied_value_name=RM%20(Metropolitana)&applied_value_order=11&applied_value_results=238")
        #driver.maximize_window()
        cookies = driver.find_element(By.XPATH, "//button[@id='cookieDisclaimerButton']")
        webdriver.ActionChains(driver).click(cookies).perform()
        driver.implicitly_wait(2)
        wait = WebDriverWait(driver, 10)
        max_iter = 100
        for i in range(max_iter):
            print(f"Scrapping page {i+1}")
            content = driver.page_source
            soup = BeautifulSoup(content, "html.parser")
            for house in soup.findAll("li", class_="ui-search-layout__item"):
                price_elem = house.find("span")
                price = [price_elem.text]
                features_elems= house.findAll("li")
                features = [elem.text for elem in features_elems]
                location_elem = house.findAll("p")
                location = [elem.text for elem in location_elem]
                all = [item.strip().lower() for  sublist in [price, features, location] for item in sublist]
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
            webdriver.ActionChains(driver)\
                .move_to_element(next_page)\
                .click(next_page).perform()
            wait.until(EC.url_to_be(next_url))  # Waiting until it's at the url clicked
            wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//li[@class='ui-search-layout__item']"))) # until all list elements can be seen

    frame = pd.DataFrame(rows)
    return frame
df = scrap_pageone()
df.to_csv("Data/houses_dirty.csv")



