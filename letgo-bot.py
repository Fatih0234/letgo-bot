import os
import time
import datetime
import re
from turkish_dates import convert_turkish_date
from collections import namedtuple
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException
import pandas as pd
from bs4 import BeautifulSoup


user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
driver_path = os.path.join(os.getcwd(), "chromedriver-win64", "chromedriver.exe")
chrome_service = Service(driver_path)
chrome_options = Options()
chrome_options.add_argument(f"user-agent={user_agent}")

browser = Chrome(service=chrome_service, options=chrome_options)
browser.implicitly_wait(7)
browser.maximize_window()

url = "https://www.letgo.com"

browser.get(url) # go to the url

time.sleep(2)
# Get to the desired location
search_query_location = "Bağcılar, Istanbul"
input_location = browser.find_element(By.XPATH, "//input[@class='_1dasd']")
input_location.click()
input_location.send_keys(Keys.CONTROL + "a")
input_location.send_keys(Keys.DELETE)
time.sleep(2)
input_location.send_keys(search_query_location)
time.sleep(2)

# find the popped up location element and click it
try:
    location_element = browser.find_element(By.XPATH, "//div[@class='_3_Rdm']")
    location_element.click()
    time.sleep(2)
except NoSuchElementException:
    print("No such location!")

# Get to the desired category
search_query_category = "iphone 11"
input_item = browser.find_element(By.XPATH, "//input[@data-aut-id='searchBox']")
input_item.click()
input_item.send_keys(Keys.CONTROL + "a")
input_item.send_keys(Keys.DELETE)
input_item.send_keys(search_query_category)
input_item.send_keys(Keys.ENTER)
time.sleep(2)


posts_html = []
go_on = True

while go_on:
    
    # let's scroll down for the page to load otherwise we don't get some attributes of the posts like the jpg images of the posts
    times_of_scroll = 5
    scrolling_weight  = browser.execute_script("return document.body.scrollHeight")/times_of_scroll
    for i in range(1,times_of_scroll):
        browser.execute_script(f"window.scrollTo(0, {(i*scrolling_weight)});")
        time.sleep(2)
    # click the load more button till we get NoSuchElementException or ElementNotInteractableException
    try:
        load_more_button = browser.find_element(By.XPATH, "//button[@data-aut-id='btnLoadMore']")
        load_more_button.click()
        time.sleep(2)
    except ElementNotInteractableException:
        go_on = False
    except NoSuchElementException:
        go_on = False

# when we get down all the load more buttons, we get all the posts
all_posts = browser.find_elements(By.XPATH, "//ul[@class='_266Ly _10aCo']")
soup = BeautifulSoup(all_posts[0].get_attribute("innerHTML"), "html.parser")
posts = soup.find_all("li", recursive=False)
posts_html.extend(posts)


letgo_list_post = namedtuple("craig_list_post", "title price post_timestamp location post_url image_url")
letgo_list_posts = []

# clean the posts_html and get the desired attributes
for post in posts_html[:-1]: # last item is not a post
    
    price_element = post.find("span", {"data-aut-id": "itemPrice"})
    price  = price_element.text if price_element else None

    title_element = post.find("span", {"data-aut-id": "itemTitle"})
    title  = title_element.text if title_element else None

    location_element = post.find("span", {"data-aut-id": "item-location"})
    location  = location_element.text if location_element else None
    
    post_timestamp_element = post.find("span", {"class": "_2jcGx"})
    post_timestamp = post_timestamp_element.text if post_timestamp_element else None
    # convert the turkish date to date format
    if post_timestamp:
        post_timestamp = convert_turkish_date(post_timestamp.upper())
        
    post_url_element = post.find("a")
    post_url = post_url_element["href"] if post_url_element else None
    post_url = f"{url}{post_url}" # add the base url to the post url

    image_url_element = post.find("img")
    image_url = image_url_element.get("src") if image_url_element else "no image"

    letgo_list_post = letgo_list_post(title, price, post_timestamp, location, post_url, image_url)
    letgo_list_posts.append(letgo_list_post) # add the post to the list

os.makedirs("results", exist_ok=True) # create a results folder if it doesn't exist

df = pd.DataFrame(letgo_list_posts)
df.to_csv(f"results/{search_query_category}_letgo_posts({datetime.datetime.now().strftime('%Y_%m_%d')}).csv", index=False)

df.to_excel(f"results/{search_query_category}_letgo_posts({datetime.datetime.now().strftime('%Y_%m_%d')}).xlsx", index=False)

browser.quit()