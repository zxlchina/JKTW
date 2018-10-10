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
#chromedriver = "/usr/local/bin/chromedriver"
chromedriver = "/usr/bin/chromedriver"


def get_content_data(driver, cid, url, source):
    driver.get(url)
    print(cid, url, source)
    print("wait for 3s ...")
    time.sleep(3) 

    print("begin handle...")
    try:
        create_time = ""
        content_sub = driver.find_element_by_class_name("article-sub")
        #解析时间
        for span in content_sub.find_elements_by_xpath(".//span"):
            if is_valid_date(span.text):
                create_time = span.text
        #解析内容
        content_data = driver.find_element_by_class_name("article-content") 
        data = content_data.get_attribute('innerHTML')
        #开始生成sql
        #print(create_time, data)
        sql = "update content_info set state=1, create_time='%s', import_time='%s', data='%s' where cid='%s'" \
         % (create_time, get_time(time.time(), "%Y-%m-%d %H:%M:%S"), escape_str(data), cid)
        print(sql)
        get_result(sql)
           
    except NoSuchElementException:
        print("Exception, no element")
        sql = "update content_info set state = 3 where cid='%s'" % cid
        print(sql)
        get_result(sql) 
    except :
        print("Exception, src:", content_sub.get_attribute('innerHTML'))
        sql = "update content_info set state = 3 where cid='%s'" % cid
        print(sql)
        get_result(sql) 
    



if __name__=='__main__':

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chrome_options=chrome_options,executable_path=chromedriver)
    driver.set_window_size(1920,1080)


    init_db()
    sql = "select cid, org_url, source from content_info where state = 0  and author not like '%悟空%' order by last_up_time desc"
    result = get_result(sql)

    index = 0
    for content in result: 
        cid = content[0]
        url = content[1]
        source = content[2]
        get_content_data(driver, cid, url, source)
        #index = index + 1 
        #if index > 10:
        #    break
        break

    driver.quit()
    

