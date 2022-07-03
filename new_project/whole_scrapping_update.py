#from ctypes import pointer
#from multiprocessing.connection import wait
#from re import search
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

def webelement_to_xpath(webelement, by):
    name = webelement.tag_name
    class_ = webelement.get_attribute(by)
    xpath = f"//{name}[@{by}='{class_}']"
    return xpath
def wainting(tag_name="div", next_url=None, last_url=None, wait=wait):
    if next_url is not None:
        wait.until(EC.url_matches(next_url))
    if last_url is not None:
        wait.until(EC.url_changes(last_url))
    wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, tag_name)))
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
        first_searchbutton = driver.find_element(
            By.XPATH, "//span[@class='andes-button__content']")
        first_searchbutton.click()
        # Segundo boton de busqueda(?)
        wainting(last_url=origin_url, wait=wait)
        menu_locator =By.XPATH, "//div[@class='ui-search-faceted-search']" 
        menu_pointer = driver.find_element(*menu_locator) # Menu de busqueda
        pointers_locator = By.XPATH, "//div[@class='ui-search-faceted-search--searchbox-dropdown']"
        offers_pointer, properties_pointer = menu_pointer.find_elements(*pointers_locator)
        search_button_locator = By.XPATH, "//button[@class='andes-button andes-button--large andes-button--loud']"
        search_button = menu_pointer.find_element(*search_button_locator)
        # Collecting all the posible variables configuration,
        # then it's just needed to change the respective url
        offers = []
        properties = []
        # Habre la lista de tipos de oferta
        webdriver.ActionChains(driver).move_to_element(offers_pointer). \
            click(). \
            perform()
        for offer_type in offers_pointer.find_elements(By.TAG_NAME, 'li'):
            offers.append(offer_type.text)
        # Habre  la lista de tipos de inmuebles
        webdriver.ActionChains(driver).move_to_element(properties_pointer). \
            click(). \
            perform()
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
                properties_pointer.click()
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
                wait.until(EC.invisibility_of_element(search_button)) # Checking if the page has change by asserting that
                    # AN elemenT on the page to change is still visible
                #wainting(wait=wait)
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
                            find_all("p")
                        location = [elem.text for elem in location_elem]
                        all_features = [item.strip().lower()
                               for item in [*types_list, price, tag, *location, *features]]
                        rows.append(all_features)
                    
                    next_page_locator = By.XPATH, "//a[@title='Siguiente' and @role='button']"
                    wainting(tag_name="button", wait=wait)
                    try:                       
                        next_page = driver.find_element(*next_page_locator)
                    except NoSuchElementException:
                        print(f"All pages scrapped from configuration {types_list[0]}-{types_list[1]}. \n"
                              f"{j+1} pages have been screpped")
                        break # Final page, there is no next button
                    wait.until(EC.element_to_be_clickable(next_page_locator))
                    next_page.click()
                    wait.until(EC.invisibility_of_element(next_page))
                    #wainting(tag_name="li", next_url=next_url, wait=wait)
                    # Waiting until it's at the url clicked
                    # until all list elements can be seen
                    #print(types_list)
                    
                # Here, when some houses search of variable's configuration ends,
                # the driver goes back to the main page(origin), where webelements are reset
                # and the next variable's configuration's search start
                menu_pointer = driver.find_element(*menu_locator)
                search_button = menu_pointer.find_element(*search_button_locator)
                offers_pointer, properties_pointer = menu_pointer.find_elements(*pointers_locator)


    df = pd.DataFrame(rows)
    return df
dataframe = scrapping_all()
dataframe.to_csv("../data/real_estate_data_raw.csv", index=False)
