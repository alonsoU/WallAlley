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
        #first_search_button = driver.find_element(By.XPATH, "//searchbox-button[@id='search-submit']")
        #webdriver.ActionChains(driver).move_to_element(first_search_button).click().perform()
        try:
                driver.find_element(
                        By.XPATH,
                        "//span[@role='button' and @class='andes-tooltip-button-close']") \
                        .click()
        except NoSuchElementException:
                pass

        menu_class = "search-bar " #"ui-search-faceted-search"
        menu_pointer = driver.find_element(By.XPATH, f"//div[@class='{menu_class}']")
        sells_pointer, properties_pointer = menu_pointer.find_elements(
                By.XPATH,
                f"//div[@class='andes-dropdown andes-dropdown--standalone  searchbox-dropdown ']") #'{menu_class}--searchbox-dropdown']")

        switch = False
        for sell_type in sells_pointer.find_elements(By.TAG_NAME, 'li'):
                webdriver.ActionChains(driver) \
                        .move_to_element(sells_pointer).click()\
                        .perform()
                driver.implicitly_wait(1)
                types_list = [sell_type.text]
                webdriver.ActionChains(driver)\
                        .move_to_element(sell_type).click() \
                        .perform()
                for property_type in properties_pointer.find_elements(By.TAG_NAME, 'li'):
                        search_button = driver.find_element(By.XPATH, "//searchbox-button[@id='search-submit']")
                        #search_button = menu_pointer.find_element(
                        #        By.XPATH,
                        #        "//button[@class='andes-button andes-button--large andes-button--loud']")
                        act = webdriver.ActionChains(driver) \
                                .move_to_element(properties_pointer).click() \
                                .perform()
                        driver.implicitly_wait(1)
                        types_list.append(property_type.text)
                        webdriver.ActionChains(driver) \
                                .move_to_element(property_type).click() \
                                .send_keys(Keys.ESCAPE) \
                                .move_to_element(search_button).click() \
                                .perform()
                        wait.until(EC.url_changes(curr_url))
                        target_url = driver.current_url
                        # At first iteration ever, this wait won't trigger
                        driver.back()
                        original_window = driver.current_window_handle
                        driver.execute_script("window.open('');")
                        driver.switch_to.window(driver.window_handles[1])
                        driver.get(target_url)
                        wait.until(EC.number_of_windows_to_be(2))
                        # All this indentated code below belongs to the scrapping of one configuration of higher
                        # variable through all pages displayed to the corresponing variables.
                        max_iter=100
                        for j in range(max_iter):
                                # This is the scrapping of just one page of the higher variables's configuration
                                print(f"Scrapping page {j + 1}")
                                content = driver.page_source
                                soup = BeautifulSoup(content, "html.parser")
                                for house in soup.findAll("li", class_="ui-search-layout__item"):
                                        price_elem = house.find("span")
                                        price = [price_elem.text]
                                        features_elems = house.findAll("li")
                                        features = [elem.text for elem in features_elems]
                                        location_elem = house.findAll("p")
                                        location = [elem.text for elem in location_elem]
                                        all = [item.strip().lower()
                                               for sublist in [price, features, location, types_list]
                                               for item in sublist]
                                        rows.append(all)
                                next_page_locator = By.XPATH, "//a[@title='Siguiente' and @role='button']"
                                try:
                                        next_page = driver.find_element(*next_page_locator)  # Two elements with the same class, Previous and Next
                                        # location = {'x': 684, 'y': 10815}
                                        next_url = next_page.get_attribute("href")
                                except NoSuchElementException:
                                        print(f"All pages seen from configuration {types_list[0]}-{types_list[1]}")
                                        break
                                wait.until(EC.element_to_be_clickable(next_page_locator))
                                webdriver.ActionChains(driver) \
                                        .move_to_element(next_page) \
                                        .click(next_page).perform()
                                wait.until(EC.url_to_be(next_url))  # Waiting until it's at the url clicked
                                wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "li"))) # until all list elements can be seen
                                break # debugging purposes
                        driver.execute_script("window.close('');")
                        driver.switch_to.window(original_window)
                        print(driver.current_url)
df = pd.DataFrame(rows)
print(df.iloc[:10,:len(df.columns)])
print(df.iloc[:10,len(df.columns):])

