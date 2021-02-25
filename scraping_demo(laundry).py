import numpy as np
from bs4 import BeautifulSoup
import selenium as sel
from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

products=[] #List to store name of the product
prices=[] #List to store price of the product
ratings=[] #List to store rating of the product
with webdriver.Chrome("C:/Users/Alonso Uribe/AppData/Local/Chromium/User Data/chromedriver.exe") as driver:
    driver.get("https://www.flipkart.com/washing-machines/fully-automatic-"
               "front-load~function/pr?sid=j9e%2Cabm%2C8qx&otracker=nmenu_sub_"
               "TVs%20%26%20Appliances_0_Fully%20Automatic%20Front%20Load")
    wait = WebDriverWait(driver, 15)
    max_iter = 100
    for i in range(max_iter):
        content = driver.page_source
        curr_url = driver.current_url
        print(f"Iteration number {i+1}")
        print(curr_url)
        soup = BeautifulSoup(content, 'html.parser')
        for a in soup.findAll('a', href=True, attrs={'class':'_1fQZEK'}):
            name = a.find('div', attrs={'class':"_4rR01T"}) # extracting the Item's compact description
            price = a.find('div', attrs={'class':'_30jeq3 _1_WHN1'}) # Item's price
            rating = a.find('div', attrs={'class':'_3LWZlK'}) # Item's rating
            products.append(name.text)
            price = int(price.text[1:].replace(',', ''))
            prices.append(price)
            if rating is not None:
                ratings.append(float(rating.text))
            else: ratings.append(np.nan)

        prev_next = driver.find_elements(By.CLASS_NAME, "_1LKTO3") # Two elements with the same class, Previous and Next
        #if i == 0: print(prev_next[0].find_element_by_tag_name("span").text)
        print(len(prev_next))
        if len(prev_next) == 1 and i > 1:
            break # breaking when hitting the last catalog page
        next_page = prev_next[-1] # 0=previous, 1=next when the driver is located between 1 and 9
        next_page_url = prev_next[-1].get_attribute("href")
        print(next_page_url)
        webdriver.ActionChains(driver).move_to_element(next_page).click().perform()
        wait.until(EC.url_to_be(next_page_url)) # Waiting until it's at the url clicked
        wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, "a")))
        wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div._4rR01T"))) # until it sees all list elements
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "_1LKTO3"))) # until the next "next" or "previous" button is clickable

table = pd.DataFrame(data={"Product": products, "Rate": ratings, "Price": prices})
table.to_csv("Data/Laundry.csv", index=False)
print(table)