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
from aip import AipSpeech
from bs4 import BeautifulSoup
import fcntl
import configparser

g_conn_inited = False

#初始化数据库
def init_db():
    global g_conn
    global g_conn_inited

    if g_conn_inited == True:
        return 0

    #读入配置文件
    cf = configparser.ConfigParser()
    cf.read("conf.conf")

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

    ret = init_db()
    if ret != 0:
        print ("init db error %d" % ret)
        return None

    try:

        cur = g_conn.cursor()
        cur.execute(sql)
        g_conn.commit()

        return cur
    except pymysql.Error as e:
        print ("MySql Error %d: %s" % (e.args[0], e.args[1]))
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

    APP_ID = '11758766'
    API_KEY = 'I5yAyCHCEw5eQhjG0nuXkgHr'
    SECRET_KEY = '8OxzRjt1dMrRgtsmTHTLpH1SxWBywoju' 

    aip_client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
    #连接超时时间
    aip_client.setConnectionTimeoutInMillis(1000)
    #数据传输超时时间
    aip_client.setSocketTimeoutInMillis(3000)


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

    
       
     
