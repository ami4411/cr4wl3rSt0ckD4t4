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

url='https://www.thestar.com.my/business/marketwatch/stock-list/?alphabet='

class DataMining:

    def alphas(self):
        alpha = []
        for letter in string.ascii_uppercase:
            alpha.append(letter)     
        alpha.append('0-9')
        print("!!!  Array of chars")
        return alpha

    def __init__(self):
        self.mydb = mysql.connector.connect(
          host="localhost",
          user="root",
          passwd="",
          database="datamining"
        )
        self.mycursor = self.mydb.cursor()
        print("!!!  Connected to db")


    def data_company(self):
        for i in self.alphas():
            print("!!!  Now char "+ i)
            browser = webdriver.Firefox(executable_path=r"C:\geckodriver\geckodriver.exe")
            browser.get(url + i)

            innerHTML = browser.execute_script('return document.body.innerHTML')
            soup = BeautifulSoup(innerHTML, 'lxml')

            stock_table = soup.find('table',{'class':'market-trans'})
            links = stock_table.findAll('a')

            company = []
            for link in links:
                start_page = requests.get('https://www.thestar.com.my'+link.get('href'))
                tree = html.fromstring(start_page.text)
                
                url_link = 'https://www.thestar.com.my'+link.get('href')
                board = tree.xpath('//li[@class="f14"]/text()')[0]
                stock_code = tree.xpath('//li[@class="f14"]/text()')[1]
                name = tree.xpath('//h1[@class="stock-profile f16"]/text()')[0]
                w52high = tree.xpath('//li[@class="f14"]/text()')[2]
                w52low = tree.xpath('//li[@class="f14"]/text()')[3]
                updateDate = tree.xpath('//span[@id="slcontent_0_ileft_0_datetxt"]/text()')[0]
                updateTime = tree.xpath('//span[@class="time"]/text()')[0]
                open_price = tree.xpath('//td[@id="slcontent_0_ileft_0_lastdonetext"]/text()')[0]
                high_price = tree.xpath('//td[@id="slcontent_0_ileft_0_opentext"]/text()')[0]
                low_price = tree.xpath('//td[@id="slcontent_0_ileft_0_lowtext"]/text()')[0]
                last_price = tree.xpath('//td[@id="slcontent_0_ileft_0_lastdonetext"]/text()')[0]
                volume = tree.xpath('//*[@id="slcontent_0_ileft_0_voltext"]/text()')[0]
                buy_vol_hundred = tree.xpath('//*[@id="slcontent_0_ileft_0_buyvol"]/text()')[0]
                sell_vol_hundred = tree.xpath('//*[@id="slcontent_0_ileft_0_sellvol"]/text()')[0]
                date_crawl = str(datetime.datetime.now())

                sql = "INSERT INTO company (url_link, board, stock_code, name, 52weekhigh, 52weeklow, date, time, open_price, high_price, low_price, last_price, volume, buy_price, sell_price, date_crawl) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                val = (url_link, board[3:],stock_code[3:], name, w52high, w52low, updateDate[10:-2],updateTime,open_price,high_price,low_price,last_price, volume, buy_vol_hundred, sell_vol_hundred, date_crawl)
                self.mycursor.execute(sql, val)
                self.mydb.commit()

                print(self.mycursor.rowcount, "record inserted at " +str(datetime.datetime.now()))

            print("!!!  Done for char "+ i)    
            browser.quit()

mining = DataMining()
mining.data_company()
    


# CREATE TABLE `company` (
#   `url_link` varchar(255) DEFAULT NULL,
#   `board` varchar(255) DEFAULT NULL,
#   `stock_code` varchar(255) DEFAULT NULL,
#   `name` varchar(255) DEFAULT NULL,
#   `52weekhigh` varchar(255) DEFAULT NULL,
#   `52weeklow` varchar(255) DEFAULT NULL,  
#   `date` varchar(255) DEFAULT NULL,
#   `time` varchar(255) DEFAULT NULL,
#   `open_price` varchar(255) DEFAULT NULL,
#   `high_price` varchar(255) DEFAULT NULL,
#   `low_price` varchar(255) DEFAULT NULL,
#   `last_price` varchar(255) DEFAULT NULL,
#   `volume` varchar(255) DEFAULT NULL,
#   `buy_price` varchar(255) DEFAULT NULL,
#   `sell_price` varchar(255) DEFAULT NULL,
#   'date_crawl` varchar(255) DEFAULT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
