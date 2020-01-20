import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
import math

#auto scroll down page
def scrollDown(browser, numberOfScrollDowns):
    body = browser.find_element_by_tag_name("body")
    while numberOfScrollDowns >=0:
        body.send_keys(Keys.PAGE_DOWN)
        numberOfScrollDowns -= 1
    return browser

#REMEBER CHANGE BOTH WHEN DOING DIFFERENT BRANDS    
#Loreal: https://shopee.sg/shop/15235546/search
#Garnier: https://shopee.sg/shop/16226024/search
#Maybelline: https://shopee.sg/shop/11719013/search

driver = webdriver.Chrome(executable_path='chromedriver')

all_brands = {"L'Oreal Paris": "https://shopee.sg/shop/15235546/search", "Garnier": "https://shopee.sg/shop/16226024/search", "Maybelline": "https://shopee.sg/shop/11719013/search"}

#initialise
brand_csv = []
category_csv =[]
titles_csv = []
prices_csv = []
review_csv=[]
product_csv = []
rating_csv =[]
date_review_csv = []

for brand in all_brands:
    brand_url = all_brands[brand]
    
    driver.get(brand_url)

    #find total number of pages
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "shopee-mini-page-controller__total")))

    no_of_pages = driver.find_element_by_class_name("shopee-mini-page-controller__total").text

    titles = []
    prices = []
    links = [] 

    #loop through each pages
    for i in range(int(no_of_pages)):
        driver.get('https://shopee.sg/shop/15235546/search?page=' + str(i))
        driver.get(brand_url + '?page=' + str(i))
        print("page " + str(i+1) )

        #get all products in the corressponding page
        timeout = 30
        try:
            WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME, "_1gkBDw")))
        except TimeoutException:
            pass

        #products = driver.find_elements_by_class_name('_1gkBDw')
        products = driver.find_elements_by_class_name('shop-search-result-view__item.col-xs-2-4')
        
        for product in (products):
            titles.append(product.find_element_by_class_name("O6wiAW").text)
            prices.append(product.find_element_by_class_name("_341bF0").text)
            links.append(product.find_element_by_css_selector('a').get_attribute('href'))
            # print("title: " + title)
            # print("price: " + price)
            # print(link)
    total = len(links)

    for i in range(len(links)):
        title = titles[i]
        price = prices[i]

        driver.get(links[i])
        print("progress: " + str(i+1) + "/" + str(total))

        timeout = 30

        driver = scrollDown(driver, 25)
        try:
            WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME, "_2aZyWI")))
        except TimeoutException:
                pass
                
        categories_holder = (driver.find_element_by_class_name("kIo6pj"))
        categories = categories_holder.find_element_by_class_name("_1z1CEl").text
        category = categories.split("\n")[-1]
        # print(category)

        timeout = 20
        try:
            WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME, "//*[@id='main']/div/div[2]/div[2]/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[1]")))
        except TimeoutException:
            pass

        #count number of ratings
        reviews_given = driver.find_elements_by_css_selector(".product-rating-overview__filter")
    
        if reviews_given != []:
            total_reviews = 0
            # reviews_given = reviews_given.split("\n")
            for star_cat in reviews_given:
                if "Star" in star_cat.text:
                    star_cat = star_cat.text
                    total_reviews += int(star_cat[star_cat.find("(")+1 : len(star_cat)-1])
            #     print(star_cat)
            # print(total_reviews)

            # total_num_reviews = driver.find_element_by_xpath('//*[@id="main"]/div/div[2]/div[2]/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[1]').text

            next_page = True
            count_review = 0

            for i in range(math.ceil(int(total_reviews)/6)):
                timeout = 25
                try:
                    WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".shopee-product-rating")))
                except TimeoutException:
                    pass

                product_reviews = driver.find_elements_by_css_selector(".shopee-product-rating")
                for product_review in product_reviews:
                    #APPEND TITLE, PRICE, CATEGORY
                    brand_csv.append(brand)
                    titles_csv.append(title)
                    prices_csv.append(price)
                    category_csv.append(category)

                    try:
                        product = product_review.find_element_by_class_name("shopee-product-rating__variation").text
                    except NoSuchElementException:
                        product = "NA"
                        
                    #APPEND PRODUCT
                    product_csv.append(product)

                    #APPEND DATE
                    date_review = product_review.find_element_by_class_name("shopee-product-rating__time").text
                    date_review_csv.append(date_review)

                    #find review
                    review = product_review.find_element_by_css_selector(".shopee-product-rating__content").text

                    #APPEND REVIEW
                    if(review != "" or review.strip()):
                        review_csv.append(review)
                    else:
                        review_csv.append("No comments/review is an image")

                    #Find star rating for each reviewer
                    rate = 0
                    ratings = product_review.find_element_by_class_name("shopee-product-rating__rating").find_elements_by_tag_name("svg")
                    for rating in ratings:
                        star = rating.get_attribute("class")
                        if star == "shopee-svg-icon icon-rating-solid--active icon-rating-solid":
                            rate += 1
                    #APPEND RATING
                    rating_csv.append(rate)
                    
                driver.find_element_by_xpath("//*[contains(@class, 'shopee-icon-button shopee-icon-button--right ')]").click()
        else:   
            brand_csv.append(brand)
            category_csv.append(category)
            titles_csv.append(title)
            prices_csv.append(price)
            review_csv.append("no reviews receive")
            product_csv.append("NA")
            rating_csv.append("NA")
            date_review_csv.append("NA")

data = {'Brand':brand_csv, 'Category': category_csv, 'Product Name ': titles_csv, 'Price':prices_csv ,'Review':review_csv, 'Product Purchase':product_csv,'Ratings':rating_csv,'Date Of Review':date_review_csv }
df = pd.DataFrame.from_dict(data)
df.to_csv('SHOPEE_ALL_BRANDS_2.csv')
driver.close()