#encoding: utf-8

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
#chrome_options.add_argument('--disable-gpu')

chromedriver = "/usr/bin/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver
driver = webdriver.Chrome(chrome_options=chrome_options,executable_path=chromedriver)
#driver = webdriver.Chrome(executable_path=chromedriver)
url = "http://www.baidu.com"
url = "https://www.toutiao.com/ch/news_tech/"
#url = "https://mbd.baidu.com/newspage/data/landingsuper?context=%7B%22nid%22%3A%22news_12232263142697479588%22%7D&n_type=0&p_from=1"
driver.get(url)
#print (driver.page_source)
#driver.save_screenshot('screen.png')
print(driver.title)
#print(driver.find_element_by_class_name("article-content"))
#print(driver.find_element_by_class_name("article-content").text)
print(driver.find_element_by_class_name("wcommonFeed").text)



driver.quit()

