from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import numpy as np
import time

def webelement_to_xpath(webelement, by):
    name = webelement.tag_name
    class_ = webelement.get_attribute(by)
    xpath = f"//{name}[@{by}='{class_}']"
    return xpath
def scrapping_all():
    rows = []
    with webdriver.Chrome("C:/Users/Alonso Uribe/AppData/Local/Chromium/User Data/chromedriver.exe") as driver:
        driver.get("https://www.portalinmobiliario.com/")
        origin_url = driver.current_url
        wait = WebDriverWait(driver, 30)
        cookies = driver.find_element(By.XPATH, "//button[@id='cookieDisclaimerButton']")
        try:
            webdriver.ActionChains(driver).click(cookies).perform()
        except NoSuchElementException:
            pass
        driver.implicitly_wait(1)
        try:
            driver.find_element(
                By.XPATH,
                "//span[@role='button' and @class='andes-tooltip-button-close']") \
                .click()
        except NoSuchElementException:
            pass

        menu_class = "searchbox"
        menu_xpath = f"//searchbox-realestate[@class='{menu_class}']"
        menu_pointer = driver.find_element(By.XPATH, menu_xpath)
        pointers_xpath = f"//searchbox-dropdown"
        sells_pointer, properties_pointer = menu_pointer.find_elements(By.XPATH, pointers_xpath)
        search_button = menu_pointer.find_element(
            By.XPATH, "//searchbox-button[@id='search-submit']"
        )
        # Collecting all the posible variables configuration,
        # then it's just needed to change the respective url
        sells = []
        properties = []
        webdriver.ActionChains(driver).move_to_element(sells_pointer). \
            click(). \
            perform()
        driver.implicitly_wait(1)
        for sell_type in sells_pointer.find_elements(By.TAG_NAME, 'li'):
            sells.append(sell_type.text)
        webdriver.ActionChains(driver).move_to_element(properties_pointer). \
            click(). \
            perform()
        driver.implicitly_wait(1)
        for property_type in properties_pointer.find_elements(By.TAG_NAME, 'li'):
            properties.append(property_type.text)
        webdriver.ActionChains(driver)\
            .move_to_element(properties_pointer).send_keys(Keys.ESCAPE).perform()

        for sell in sells:
            webdriver.ActionChains(driver).move_to_element(sells_pointer).click().perform()
            for x in sells_pointer.find_elements(By.TAG_NAME, "li"):
                if x.text == sell:
                    sell_type = x
                    break
            webdriver.ActionChains(driver).move_to_element(sell_type).click() \
                .send_keys(Keys.ESCAPE) \
                .perform()
            for property in properties:
                webdriver.ActionChains(driver).move_to_element(properties_pointer).click() \
                    .perform()
                for y in properties_pointer.find_elements(By.TAG_NAME, "li"):
                    if y.text == property:
                        property_type = y
                        break
                else:
                    continue
                webdriver.ActionChains(driver).move_to_element(property_type).click() \
                    .send_keys(Keys.ESCAPE) \
                    .move_to_element(search_button) \
                    .click() \
                    .perform()
                wait.until(EC.url_changes(origin_url))
                max_iter = 100
                types_list = [sell, property]
                for j in range(max_iter):
                    # This is the scrapping of just one page of the higher variables's configuration
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
                        next_page = driver.find_element(
                            *next_page_locator)  # Two elements with the same class, Previous and Next
                        next_url = next_page.get_attribute("href")
                    except NoSuchElementException:
                        print(f"All pages scrapped from configuration {types_list[0]}-{types_list[1]}. \n"
                              f"{j+1} pages have been screpped")
                        break # Final page, there is no next button
                    wait.until(EC.element_to_be_clickable(next_page_locator))
                    webdriver.ActionChains(driver) \
                        .move_to_element(next_page) \
                        .click(next_page).perform()
                    wait.until(
                        EC.url_to_be(next_url))  # Waiting until it's at the url clicked
                    wait.until(
                        EC.presence_of_all_elements_located((By.TAG_NAME, "li")))  # until all list elements can be seen
                    #print(types_list)
                    #break # debugging
                # Here, when some houses search of variable's configuration ends,
                # the driver goes back to the main page(origin), where webelements are reset
                # and the next variable's configuration's search start
                driver.get(origin_url)
                wait.until(EC.url_to_be(origin_url))
                wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "li")))
                menu_pointer = driver.find_element(By.XPATH, menu_xpath)
                search_button = menu_pointer.find_element(
                    By.XPATH, "//searchbox-button[@id='search-submit']"
                )
                sells_pointer, properties_pointer = menu_pointer.find_elements(By.XPATH, pointers_xpath)

    df = pd.DataFrame(rows)
    return df
dataframe = scrapping_all()
dataframe.to_csv("Data/all_house_data_raw.csv", index=False)
