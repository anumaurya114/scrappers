import bs4
from crawler import Crawler
import pandas as pd
import re 
from urllib.parse import urljoin
import queue
import threading
import json 
import threading
import time
import queue

from selenium.webdriver.common.keys import Keys

# # Create and start the initial threads
initial_thread_count = 4
lock = threading.Lock()
taskQueue = queue.Queue()
taskQueue2 = queue.Queue()
BASE_URL = "https://www.amazon.in/"
HOME_PAGE = "https://www.amazon.in/gp/bestsellers/hpc"
# BASE_URL = "https://web.archive.org/web/20230401054228/https://www.amazon.in/"
# HOME_PAGE = "https://web.archive.org/web/20230401054228/https://www.amazon.in/gp/bestsellers/hpc"
def getCats():
    def loadCats():
        cats = json.load(open(f"cats.json","r"))
        return cats 

    def saveCats(cats):
        json.dump(cats, open(f"cats.json","+w"))

    try:
        cats = loadCats()
    except:
        saveCats({})
        cats = loadCats()
        crawler = Crawler()
        page = crawler.getPage(HOME_PAGE)
        pageSource = page.page_source
        soup = bs4.BeautifulSoup(pageSource, 'lxml')

        for child in soup.find("div",attrs={"role":"group"}).children:
            url = child.find('a')['href']
            subcategory = child.get_text()
            cats[subcategory] = url

    saveCats(cats)
    return cats


cats = getCats()
subcategoryList = list(cats.keys())


def loadData():
    data = json.load(open(f"data.json","r"))
    return data

def saveData(data):
    json.dump(data, open(f"data.json","+w"))

def loadRatingData():
    data = json.load(open(f"rating.json","r"))
    return data

def saveRatingData(data):
    with lock:
        json.dump(data, open("rating.json","+w"))



print(f"total name {len(subcategoryList)}")
import time
t = time.time()
try:
    data = loadData()
    print("data exists")
except:
    saveData({})
    data = loadData()

def crawOver(subCategory):
    global data
    name = subCategory
    print("###"*3)
    print(f"subCategory {subCategory}")
    crawler = Crawler()
    t = time.time()
    catUrl = cats[name]

    
    page = crawler.getPage(urljoin(BASE_URL, catUrl))
    
    crawler.pause(10)

    productsData = data.get(name, {})
    if len(productsData)==100:
        print(subCategory, "already scraped")
    else:
        print(subCategory,len(productsData))

    while True:
        #get data
        if len(productsData.keys())>=100:
            break
        else:
            print("Current product data", len(productsData.keys()))
        pageSource = page.page_source
        soup = bs4.BeautifulSoup(pageSource, 'lxml')
        last_height = page.execute_script("return document.body.scrollHeight")
        lastPageNumber = 0
        for product in soup.find_all('div',attrs={"id":"gridItemRoot"}):
            productRank = product.find('span',attrs={"class":"zg-bdg-text"}).get_text()
            productData = productsData.get(productRank,{})

            productUrl  = product.find("a")["href"]
            try:
                price = product.find("span", attrs={"class":"a-color-price"}).get_text()
            except:
                print(productUrl)
                price = ''
            try:
                ratingCount = product.find("span",attrs={"class":"a-size-small"}).get_text()
            except:
                ratingCount = ''
            productData['productRank'] = productRank
            productData['productUrl'] = productUrl
            productData['price'] = price 
            productData['ratingCount'] = ratingCount
            productData['productName'] = product.get_text()



            productsData[productRank] = productData
        new_height_try = (last_height + 300)
        page.execute_script(f"window.scrollTo(0, {new_height_try});")

        # Wait to load page
        crawler.pause(10)

        # Calculate new scroll height and compare with last scroll height
        new_height = page.execute_script("return document.body.scrollHeight")
        try:
            pageNumber = page.current_url.split("&")[1].split("=")[1]
        except:
            pageNumber = 1
        if new_height == last_height:
            try:
                elem = page.find_element_by_class_name(name="a-last")
                elem.click()
            except:
                pass
        
            if pageNumber==lastPageNumber:
                pass
        lastPageNumber = pageNumber
        last_height = new_height

    data[name] = productsData
    saveData(data)
    print("Saving category data", len(productsData.keys()))
        
    crawler.getDriver().close()

def getRatingData(url, ind, productsData, subCategory, data, indSubCat, crawler):
    global ratingData, TOTAL
    TOTAL += 1
    print({"url":url,"ind":ind, "total":len(productsData), "subCategory":subCategory, "Total Sub Cats ": len(list(data.keys())), "sub cat serial": indSubCat})
    if TOTAL%5==0:
        saveRatingData(ratingData)
    
    page = crawler.getPage(urljoin(BASE_URL, url))
    crawler.pause(5)
    new_height_try = (page.execute_script("return document.body.scrollHeight") + 300)
    page.execute_script(f"window.scrollTo(0, {new_height_try});")
    crawler.pause(5)

    # Find the target element you want to scroll to (replace with your own locator)
    target_element = None
    # Scroll until the target element is visible
    while not target_element:
        # Execute JavaScript to scroll down the page
        try:
            target_element = page.find_element_by_class_name(name='a-span9') 
            brandName = target_element.text
        except:
            target_element = None
            new_height_try = (page.execute_script("return document.body.scrollHeight") + 1000)
            page.execute_script(f"window.scrollTo(0, {new_height_try});")
            crawler.pause()


    target_element = None
    # Scroll until the target element is visible
    while not target_element:
        # Execute JavaScript to scroll down the page
        try:
            target_element = page.find_element_by_class_name(name="rhf-sign-in-title") 
        except:
            target_element = None
            new_height_try = (page.execute_script("return document.body.scrollHeight") + 1000)
            page.execute_script(f"window.scrollTo(0, {new_height_try});")
            crawler.pause(5)

            # Wait to load page

            # Calculate new scroll height and compare with last scroll height
            
    pageSource = page.page_source
    soup = bs4.BeautifulSoup(pageSource, 'lxml')
    divs = soup.find_all('div')
    reviews = []
    for div in divs:
        if "customer_review" in div.get('id',""):
            try:
                rating = div.find(attrs={"data-hook":"review-star-rating"}).get_text()
            except:
                rating = ''
            
            try:
                remark = div.find(attrs={"class":"a-letter-space"}).find_next('span').get_text()
            except:
                remark = ""
            try:
                date = div.find(attrs={"data-hook":"review-date"}).get_text()
            except:
                date = ''
            
            try:
                reviewSummary = div.find(attrs={"data-hook":"review-collapsed"}).get_text()
            except:
                reviewSummary = ''

            reviewData = {"rating":rating, "remark":remark, "date":date, 'reviewSummary':reviewSummary, 
                          "brandName":brandName}
            reviews.append(reviewData)
            print(brandName)
    ratingData[url] = reviews


for subCategory in subcategoryList:
    if len(data.get(subCategory,{}))!=100:
        taskQueue.put(subCategory)
    






# Function to create and run a new thread
def run_thread():
    while True:
        try:
            task = taskQueue.get(timeout=3)
        except:
            return
        
        subCategory = task
        crawOver(subCategory)

# Function to create and run a new thread
def run_thread2(crawler):
    while True:
        try:
            task = taskQueue2.get(timeout=3)
        except:
            return
        url = task['url']
        ind = task['ind'] 
        productsData = task['productsData'] 
        subCategory = task['subCategory']
        data = task['data']
        indSubCat = task['indSubCat']


        getRatingData(url, ind, productsData, subCategory, data, indSubCat, crawler)

threads = []
for i in range(initial_thread_count):
    thread = threading.Thread(target=run_thread)
    thread.start()
    threads.append(thread)


# Wait for all threads to complete
for thread in threads:
    thread.join()

data = loadData()

try:
    ratingData = loadRatingData()
except:
    ratingData = {}  
remaining = 0
for indSubCat, key in enumerate(list(data.keys())):
    subCategory = key 
    productsData = data.get(subCategory, {})
    for ind, product in enumerate(list(productsData.values())):
        if len(ratingData.get(product['productUrl'],[]))>0:
            continue
        url = product['productUrl']
        remaining += 1
        print(urljoin(BASE_URL, url))
        taskQueue2.put({"url":url,"ind":ind, "productsData":(productsData), "subCategory":subCategory, "data": data, "indSubCat": indSubCat})
print("remaining", remaining)
  
threads = []
TOTAL = 0
crawlers = [Crawler(headLess=False) for i in range(initial_thread_count)]
for i in range(initial_thread_count):
    thread = threading.Thread(target=run_thread2, args=(crawlers[i],))
    thread.start()
    threads.append(thread)


for i in range(initial_thread_count):
    threads[i].join()
    crawlers[i].getDriver().close()










