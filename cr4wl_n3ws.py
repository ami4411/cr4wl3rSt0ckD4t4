from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from lxml import html
import requests
from bs4 import BeautifulSoup
import string
import re
import pandas as pd
import os
import mysql.connector
import datetime

urlNews='https://kls3.i3inv3st0r.com/jsp/n3wshl.jsp'
urlBlogs='https://kls3.i3inv3st0r.com/jsp/bl0g/bl0ghl.jsp'

class DataMining:

    def __init__(self):
        self.mydb = mysql.connector.connect(
          host="localhost",
          user="root",
          passwd="",
          database="datamining"
        )
        self.mycursor = self.mydb.cursor()
        print("!!!  Connected to db")


    def news_company(self):
            print("!!! START CRAWLING NEWS")

            browser = webdriver.Firefox(executable_path=r"C:\geckodriver\geckodriver.exe")
            browser.get(urlNews)

            innerHTML = browser.execute_script('return document.body.innerHTML')
            soup = BeautifulSoup(innerHTML, 'lxml')

            date = soup.select('div > h3')

            for a in date:
                print(" ")
                print(a.text)
                div = soup.find('h3', text=a.text).find_next_siblings('ul')[0]
                title = div.find_all('a')
              
                for b in title:
                    time_raw = b.find_next_siblings('span', {'class': 'graydate'})[0].text
                    time = time_raw[3:].strip()

                    dateInsert = str(datetime.datetime.now())
                    tarikh = a.text
                    tajuk = b.text
                    penulis = None
                    category = "news"
                    
                    print(b.text)
                    print(time)             
                    
                    sql = "INSERT INTO newsblog (date_insert, date_publish, time_publish, title, author, category) VALUES (%s,%s,%s,%s,%s,%s)"
                    val = (dateInsert, tarikh, time, tajuk, penulis, category)
                    self.mycursor.execute(sql, val)
                    self.mydb.commit()

            browser.quit()

    def blog_company(self):
            print("!!! START CRAWLING BLOG")

            browser = webdriver.Firefox(executable_path=r"C:\geckodriver\geckodriver.exe")
            browser.get(urlBlogs)

            innerHTML = browser.execute_script('return document.body.innerHTML')
            soup = BeautifulSoup(innerHTML, 'lxml')

            date = soup.find("div", {"id": "maincontent730"}).find_all('h3')
            print(date)

            for a in date:
                print(" ")
                # print(a.text)

                data_ul = soup.find('h3', text=a.text).find_next_siblings('ul')[0]
                # print(div)
                data_li = data_ul.select('ul > li')
                # print(title)
                for b in data_li:

                    title = b.find('a')
                    author = b.find('span', {'class': 'comuid'})
                    all_text = b.find('span', {'class': 'graydate'}).text
                    child_text = b.find('span', {'class': 'comuid'}).text
                    parent_text = all_text.replace(child_text, '')
                    # print(" ")
                    # print("Title: "+ title.text)
                    # print("Author: "+ author.text)
                    # print(time)
                    dateInsert = str(datetime.datetime.now())
                    tarikh = a.text
                    tajuk = title.text
                    penulis = author.text
                    category = "blog"
                    time = parent_text[5:].strip()

                    sql = "INSERT INTO newsblog (date_insert, date_publish, time_publish, title, author, category) VALUES (%s,%s,%s,%s,%s,%s)"
                    val = (dateInsert, tarikh, time, tajuk, penulis, category)
                    self.mycursor.execute(sql, val)
                    self.mydb.commit()

                print("!!! END CRAWLING BLOG FOR TODAY")

                break;

            browser.quit()        

mining = DataMining()
mining.blog_company()
# mining.news_company()
    
# https://linuxhint.com/find_children_nodes_beautiful_soup/

# CREATE TABLE `newsblog` (
#   `date_crawl` varchar(255) DEFAULT NULL,
#   `date_publish` varchar(255) DEFAULT NULL,
#   `time_publish` varchar(255) DEFAULT NULL,
#   `title` text DEFAULT NULL,
#   `author` varchar(255) DEFAULT NULL,
#   `category` varchar(255) DEFAULT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
