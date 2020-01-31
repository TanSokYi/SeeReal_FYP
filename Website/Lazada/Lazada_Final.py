import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import time


#1.Loreal
#https://www.lazada.sg/l-oreal-paris-official-store/?langFlag=en&q=All-Products&from=wangpu&pageTypeId=2
#2.Garnier
#https://www.lazada.sg/garnier-official-store/?langFlag=en&q=All-Products&from=wangpu&pageTypeId=2
#3.Maybelline
#https://www.lazada.sg/maybelline-official-store/?langFlag=en&q=All-Products&from=wangpu&pageTypeId=2

#Open Chrome
driver = webdriver.Chrome(executable_path='chromedriver')

#initalise
brand_csv=[]
category_csv =[]
titles_csv = []
prices_csv = []
review_csv=[]
product_csv = []
rating_csv =[]
date_review_csv = []

brand = ['L-oreal-Paris','Garnier', 'Maybelline']
for i in range(len(brand)):
    driver.get('https://www.lazada.sg/'+brand[i]+'-official-store/?langFlag=en&q=All-Products&from=wangpu&pageTypeId=2')
    brand_name = brand[i]

    categories = driver.find_elements_by_class_name('cds557')
    main_cat =[]

    for category in categories:
        main_cat_link = category.get_attribute('href')
        main_cat.append(main_cat_link)
    

    for i in range(len(main_cat)):
        titles = []
        prices = []
        urls = []   
        category_type=[]

        driver.get(main_cat[i])
    
        category = driver.find_element_by_class_name('c2BJaq').text
        print("Category:" + category)
        products = driver.find_elements_by_class_name('c2prKC')

        for product in products:
            
            category_type.append(category)
            titles.append(product.find_element_by_class_name('c16H9d').text)
            prices.append(product.find_element_by_class_name('c3gUW0').text)

            #retrieve each product's link
            link = product.find_element_by_class_name('c16H9d').find_element_by_css_selector('a').get_attribute('href')
            urls.append(link)

        #retrieve each product's reviews
        for i in range(len(urls)):   
            driver.get(urls[i])
            print('Progess:',i+1,'/',len(titles))

            while True:
                timeout = 30
                try:
                   WebDriverWait(driver,10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR,"div.item")))
                except TimeoutException:
                    pass

                try:
                    #Get the review details here
                    product_reviews = driver.find_elements_by_css_selector("[class='item']")
               
                    # Get product review
                    for product_review in product_reviews:
                        brand_csv.append(brand_name)
                        category_csv.append(category_type[i])
                        titles_csv.append(titles[i])
                        prices_csv.append(prices[i])

                        review = product_review.find_element_by_css_selector("[class='content']").text
                        if (review != "" or review.strip()):
                            review_csv.append(review)
                        else:
                            review_csv.append("No comments/review is an image")

                        # Product Purchase
                        # Check if the product purchase exists
                        try:
                            product_purchase = product_review.find_element_by_css_selector("[class='skuInfo']").text
                            product_csv.append(product_purchase)
                        except NoSuchElementException:
                            product_csv.append("NA")

                        # Star rating
                        star_ratings = product_review.find_elements_by_css_selector("[class='star']")
                        stars = "https://laz-img-cdn.alicdn.com/tfs/TB19ZvEgfDH8KJjy1XcXXcpdXXa-64-64.png"

                        star_rate = 0
                        for rating in star_ratings:
                            # print(rating.get_attribute('src'))
                            if (rating.get_attribute('src') == stars):
                                star_rate = star_rate + 1
                        rating_csv.append(star_rate)

                        # Date of Review
                        date = product_review.find_element_by_css_selector("[class='title right']").text
                        date_review_csv.append(date)

                        print("1 Entry")
                except:
                    break
                try:
                    #Check for next_Page button
                    next_page_bar = driver.find_element_by_css_selector("[class = next-pagination-pages")
                    #Check for button next-pagination-item have disable attribute then jump from loop else click on the next button
                    if len(driver.find_elements_by_css_selector("button.next-pagination-item.next[disabled]"))>0:
                        break
                    else:
                        button_next=WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button.next-pagination-item.next")))
                        driver.execute_script("arguments[0].click();", button_next)
                        print("next page")
                        time.sleep(2)
                except:
                    break

data = {'Brand': brand_csv, 'Category': category_csv, 'Product Name ': titles_csv, 'Price':prices_csv ,'Review':review_csv, 'Product Purchase':product_csv,'Ratings':rating_csv,'Date Or Review':date_review_csv}
df_makeup = pd.DataFrame.from_dict(data)
df_makeup.to_csv('Lazada_Product.csv')
driver.close()

