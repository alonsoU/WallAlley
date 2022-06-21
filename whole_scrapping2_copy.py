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
        wait = WebDriverWait(driver, 10)
        try:
            cookies = driver.find_element(By.XPATH, "//button[@id='newCookieDisclaimerButton']")
            webdriver.ActionChains(driver).click(cookies).perform()
        except NoSuchElementException:
            pass
        #driver.implicitly_wait(1) # No lo veo necesario
        # Primer boton de busqueda
        driver.find_element(
            By.XPATH,
            f"//span[@class='andes-button__content']") \
            .click()

        # Segundo boton de busqueda(?)
        wait.until(EC.url_changes(origin_url))
        menu_xpath = f"//div[@class='ui-search-faceted-search']" 
        menu_pointer = driver.find_element(By.XPATH, menu_xpath) # Menu de busqueda
        offers_pointer, properties_pointer = menu_pointer.find_elements(By.XPATH,
            "//div[@class='ui-search-faceted-search--searchbox-dropdown']"
            )
        search_button = menu_pointer.find_element(By.XPATH,
            "//button[@class='andes-button andes-button--large andes-button--loud']"
            )
        # Collecting all the posible variables configuration,
        # then it's just needed to change the respective url
        offers = []
        properties = []
        # Habre la lista de tipos de oferta
        webdriver.ActionChains(driver).move_to_element(offers_pointer). \
            click(). \
            perform()
        driver.implicitly_wait(1)
        for offer_type in offers_pointer.find_elements(By.TAG_NAME, 'li'):
            offers.append(offer_type.text)
        # Habre  la lista de tipos de inmuebles
        webdriver.ActionChains(driver).move_to_element(properties_pointer). \
            click(). \
            perform()
        driver.implicitly_wait(1)
        for property_type in properties_pointer.find_elements(By.TAG_NAME, 'li'):
            properties.append(property_type.text)
        webdriver.ActionChains(driver)\
            .move_to_element(properties_pointer).send_keys(Keys.ESCAPE).perform()

        # Recorriendo todo tipo de oferta
        for offer in offers:
            webdriver.ActionChains(driver).move_to_element(offers_pointer).click().perform()
            # Compara la config del menu con 
            for x in offers_pointer.find_elements(By.TAG_NAME, "li"):
                if x.text == offer:
                    offer_type = x # Pointer actual guardado
                    break
            # Clickeando pointer actual y cerrando la lista
            webdriver.ActionChains(driver).move_to_element(offer_type).click() \
                .send_keys(Keys.ESCAPE) \
                .perform()
            for property in properties:
                webdriver.ActionChains(driver).move_to_element(properties_pointer).click() \
                    .perform()
                for y in properties_pointer.find_elements(By.TAG_NAME, "li"):
                    if y.text == property:
                        property_type = y # Pointer actual guardado
                        break # La idea en estos dos ultimos breaks es alinear los
                              # pointer con las tupla fe oferta (ej: {Ventas, Departamentos})
                # 'else' de contención. Sigue a la siguiente combinación, por si no existe
                else:
                    webdriver.ActionChains(driver).move_to_element(properties_pointer).click()\
                    .perform()
                    continue
                webdriver.ActionChains(driver).move_to_element(property_type).click() \
                    .send_keys(Keys.ESCAPE) \
                    .move_to_element(search_button) \
                    .click() \
                    .perform()
                #wait.until(EC.url_changes(origin_url))
                max_iter = 100
                types_list = [offer, property]
                for j in range(max_iter):
                    # This is the scrapping of just one page of the higher variables's configuration
                    content = driver.page_source
                    soup = BeautifulSoup(content, "html.parser")
                    for house in soup.findAll("li", class_="ui-search-layout__item"):
                        price_elem = house.find("span", class_="price-tag-fraction")
                        price = price_elem.text
                        tag_elem = house.find("span", class_="price-tag-symbol")
                        tag = tag_elem.text
                        features_elems = house.find_all("li", class_="ui-search-card-attributes__attribute")
                        features = [elem.text for elem in features_elems]
                        location_elem = house.find("div", class_="ui-search-item__group ui-search-item__group--location"). \
                            find("p")
                        location = [elem.text for elem in location_elem]
                        all_features = [item.strip().lower()
                               for item in [price, tag, *features, *location, *types_list]]
                        rows.append(all_features)
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
