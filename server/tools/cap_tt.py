#encoding: utf-8

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from commonlib import *
import time
import os
import sys
import json


#chrome headless path
#chromedriver = "C:\Program Files\Python36\chromedriver.exe"
chromedriver = "/usr/bin/chromedriver"
map_content = {}

#开始分析文章信息
def analysis(driver):
    global map_content      #保存所有的内容
    
    feeds = driver.find_element_by_class_name("wcommonFeed")
    for feed in feeds.find_elements_by_xpath(".//li"):
        content = {}
        try:
            alist = feed.find_elements_by_xpath(".//a")
            for a in alist:
                class_name = a.get_attribute("class")
                if class_name is None:
                    continue

                if class_name.find("title") >= 0:  #标题        
                    #print("title:", a.text, a.get_attribute("href"))
                    content["title"] = a.text
                    content["url"] = a.get_attribute("href")
                    #print (content["url"])
                elif class_name.find("source") >= 0:  #来源
                    #print("source:", a.text, a.get_attribute("href"))
                    content["author"] = a.text
                    content["author_url"] = a.get_attribute("href")
                elif class_name.find("img-wrap") >= 0:  #头图
                    img = a.find_element_by_xpath(".//img")
                    content["img"] = img.get_attribute("src")
        except NoSuchElementException:
            print("Exception, src:", feed.get_attribute('innerHTML'))
            continue
        except :
            print("Exception, src:", feed.get_attribute('innerHTML'))
        
        if "url" in content:
            if content["url"].find("www.toutiao.com/group/") >=0:   #判断是否是文章的url
                map_content[content["url"]] = content
                #print(content)    



def get_id_from_url(url):
    items = url.split("/")
    if len(items) < 2:
        return None
    return items[len(items)-2]


def save_db(map_content):
    #下面开始保存db
    init_db()

    for url in map_content:
        content = map_content[url] 
        cid = get_id_from_url(url)

        if cid is None:
            print("Invalid url, url:", url)
            continue

        cid = "tt_" + cid
        title = ""
        url = ""
        author = ""
        author_url = ""
        img = ""

        if "title" in content:
            title = content["title"]

        if "url" in content:
            url = content["url"]

        if "author" in content:
            author = content["author"] 

        if "author_url" in content:
            author_url = content["author_url"] 

        if "img" in content:
            img = content["img"] 

        sql = "insert into content_info (cid, title, org_url, author, author_url, head_img, state, source) values ('%s', '%s', '%s', '%s', '%s', '%s', 0, 'toutiao')" % \
               (cid, title, url, author, author_url, img)

        print(sql)
        get_result(sql)



def save_cookie(driver):
    cookies = driver.get_cookies()
    jsonCookies = json.dumps(cookies)
    with open('cookies.json', 'w') as f:
        f.write(jsonCookies)


def load_cookie(driver):
    #检查文件是否存在
    if not os.path.exists("cookies.json"):
        return 

    #删除第一次建立连接时的cookie
    driver.delete_all_cookies()
    #读取登录时存储到本地的cookie
    with open('cookies.json', 'r', encoding='utf-8') as f:
        listCookies = json.loads(f.read())

    for cookie in listCookies:
        driver.add_cookie({
                'domain': cookie['domain'],
                'name': cookie['name'],
                'value': cookie['value'],
                'path': '/',
                'expires': None
                })


if __name__=='__main__':

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chrome_options=chrome_options,executable_path=chromedriver)
    driver.set_window_size(1920,1080)
    
    url = "https://www.toutiao.com/ch/news_tech/"
    driver.get(url)
    print("load cookie ...")
    load_cookie(driver)
   
    #js="var q=document.documentElement.scrollTop=100000"
    #driver.execute_script(js)    
    #print (driver.page_source)
    #driver.save_screenshot('screen.png')
    
    try:
        for i in range(1):
            driver.get(url)
            print("wait for 3s ...")
            time.sleep(3)
     
            map_content = {}
            print("---------------------------------------")
            analysis(driver)
            #print("before refresh")
            #refresh = driver.find_element_by_class_name("tool-item")
            #refresh.click()
            #time.sleep(3)
            print ("before save db ...")
            save_db(map_content)
    except:                
        print ("Exception ...") 
    finally:
        save_cookie(driver)
        driver.quit()
    

