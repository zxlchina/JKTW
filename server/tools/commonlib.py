#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Author: 
# Created Time: 2017-09-22 08:42:33
# Description: 

import os
import pymysql
import sys
import time
import datetime
import base64
import json
import urllib
import hashlib
import requests
from aip import AipSpeech
from aip import AipOcr
from bs4 import BeautifulSoup
import fcntl
import configparser
import threading

g_conn_inited = False
g_sql_lock = threading.Lock()

#初始化数据库
def init_db(conf_file="conf.conf"):
    global g_conn
    global g_conn_inited

    if g_conn_inited == True:
        #ping一下db
        need_init = False
        try:
            g_conn.ping(False)
            #print("after ping")
        except:
            print("ping Error! need init")
            need_init = True
            
        #不需要初始化
        if not need_init:
            #print ("do not need init")
            return 0

    #读入配置文件
    cf = configparser.ConfigParser()
    cf.read(conf_file)

    chost = cf.get("db", "host")
    cuser = cf.get("db", "user")
    cpasswd = cf.get("db", "password")
    cport = int(cf.get("db", "port"))
    ccharset = cf.get("db", "charset")
    cdbname = cf.get("db", "dbname")


    try:
        g_conn = pymysql.connect(host=chost, user=cuser, passwd=cpasswd, port=cport, charset=ccharset)
        g_conn.select_db(cdbname)

        g_conn_inited = True
    except pymysql.Error as e:
        print ("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        return -1
    return 0

#查询sql
def get_result(sql):
    global g_conn
    global g_conn_so
    global g_sql_lock 

    g_sql_lock.acquire() 

    ret = init_db()
    if ret != 0:
        print ("init db error %d" % ret)
        g_sql_lock.release()
        return None

    try:

        cur = g_conn.cursor()
        cur.execute(sql)
        g_conn.commit()

        g_sql_lock.release()

        return cur
    except pymysql.Error as e:
        print ("MySql Error %d: %s" % (e.args[0], e.args[1]))

        g_sql_lock.release()
        return None


def escape_str(s):
    return g_conn.escape_string(s)

def run_cmd(cmd):
    p = os.popen(cmd, 'r')



def get_date(timestamp):
    timeArray = time.localtime(timestamp)
    date = time.strftime("%Y%m%d", timeArray)
    return  date

def get_time(timestamp, fmt = "%Y%m%d%H%M%S"):
    timeArray = time.localtime(timestamp)
    date = time.strftime(fmt, timeArray)
    return  date


def get_day_of_day(n=0):
    if (n < 0):
        n = abs(n)
        return date.today() - timedelta(days=n)
    else:
        return date.today() + timedelta(days=n)


def get_day_start(day):
   return datetime.datetime(day.year, day.month, day.day) 


def cal_day_gap(start, end):
    delta = end - start
    return delta.days + delta.seconds / 86400.0


def is_valid_date(date):
    try:
        if ":" in date:
            time.strptime(date, "%Y-%m-%d %H:%M:%S")
        else:
            time.strptime(date, "%Y-%m-%d")
        return True
    except:
        return False



def init_aip():
    global aip_client
    global aip_client_ocr

    APP_ID = '11758766'
    API_KEY = 'I5yAyCHCEw5eQhjG0nuXkgHr'
    SECRET_KEY = '8OxzRjt1dMrRgtsmTHTLpH1SxWBywoju' 

    aip_client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

    #连接超时时间
    aip_client.setConnectionTimeoutInMillis(1000)
    #数据传输超时时间
    aip_client.setSocketTimeoutInMillis(3000)





    APP_ID = '14462175'
    API_KEY = 'KG8eaIU0ouFCaMLnQZ2u3IX1'
    SECRET_KEY = 'waX99HpVyaukCX6aruuazGNo6zaVOcVu' 
    aip_client_ocr = AipOcr(APP_ID, API_KEY, SECRET_KEY)


def get_tts(data, out_file_name,spd = 5, pit = 5, vol = 5, per = 3):
    result = aip_client.synthesis(data, 'zh', 1, {
        'spd': spd ,
        'pit': pit,
        'vol': vol,
        'per': per 
    })

    if not isinstance(result, dict):
        with open(out_file_name, 'wb') as f:
            f.write(result)
    else:
        return False
    
    return True



def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


#得到图片中的车牌号，百度
def get_car_number(filename):
    image = get_file_content(filename)
    options = {}
    options["multi_detect"] = "true"
    res = aip_client_ocr.licensePlate(image, options) 

    return res


def get_sign(params):
    uri_str = ""
    for key in sorted(params.keys()):
        if key == "app_key":
            continue
        uri_str += "%s=%s&" % (key, urllib.parse.quote(str(params[key]), safe = ""))
    sign_str = uri_str + "app_key=" + params["app_key"]

    hash_md5 = hashlib.md5(sign_str.encode())
    return hash_md5.hexdigest().upper()
 

#优图根据图片得到车牌号
def get_car_number_by_youtu(img_url):
    params = {}
    url = "https://api.ai.qq.com/fcgi-bin/ocr/ocr_plateocr"
    with open(img_url, "rb") as img_file:
        image_data = img_file.read()

    bs64 = base64.b64encode(image_data)
    params["image"] = bs64.decode("utf-8")
    params["app_id"] = 2109009601
    params["app_key"] = "j3uUlfX3KWokWLe4"
    #params["image_url"] = img_url
    params["time_stamp"] = str(int(time.time()))
    params["nonce_str"] = str(int(time.time()))
    params["sign"] = get_sign(params)

    data = ""
    for key in params:
        data += "%s=%s&" % (key, params[key])

    response = requests.post(url, data=params) 
    res = response.text

    print(res)
    
    car_number_list = []
    try:
        data = json.loads(res)
        if data["ret"] != 0:
            print ("get car number error:" ,res)
            return []

        for item in data["data"]["item_list"]:
            car_number_list.append(item["itemstring"])
    except :
        print("json exception")
        return []

    return car_number_list




def get_text_from_html(html):
    soup = BeautifulSoup(html)
    return soup.get_text()



def find_token(cutlist, word):
    if word in cutlist:
        return True
    else:
        return False

def cut(cutlist, lines):
    res = []
    s = []
    for word in lines:
        if find_token(cutlist, word):
            s.append(word)
            sstr = (''.join(s)).strip(" ")
            if sstr != "":
                res.append(sstr)
            s = []
        else:
            s.append(word)
    return res
    

def get_sentence(data):
    cutlist ="。！？!?"
    sentences = []

    lines = data.split("\n")
    for line in lines:
        sts = cut(list(cutlist), line)
        for s in sts:
            sentences.append(s)

    return sentences
        

def try_lock(lock_file):
    global lockfile 
    lockfile = open(lock_file, "w+") 
    try:
        fcntl.flock(lockfile.fileno(), fcntl.LOCK_NB | fcntl.LOCK_EX)
    except:
        return False
    return True

    
       
     
