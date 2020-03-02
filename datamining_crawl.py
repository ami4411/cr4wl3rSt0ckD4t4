from selenium import webdriver
from lxml import html
import requests
from bs4 import BeautifulSoup
import string
import mysql.connector
import datetime

from selenium.webdriver.support.ui import WebDriverWait

urlTheStar='https://www.thestar.com.my/business/marketwatch/stock-list/?alphabet='
urlNews='https://klse.i3investor.com/jsp/newshl.jsp'
urlBlogs='https://klse.i3investor.com/jsp/blog/bloghl.jsp'
urlQuarter='https://klse.i3investor.com/financial/quarter/latest.jsp'

alpha = []
for letter in string.ascii_uppercase:
    alpha.append(letter)     
alpha.append('0-9')
print("!!!  Array of chars")
print(alpha)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database="datamining"
)
mycursor = mydb.cursor()
print("!!!  Connected to db")


##############################
#   START CRAWLING STOCK
##############################
for i in alpha:
    print("!!!  Now char "+ i)
    browser = webdriver.Firefox(executable_path=r"C:\geckodriver\geckodriver.exe")
    browser.get(urlTheStar + i)

    innerHTML = browser.execute_script('return document.body.innerHTML')
    soup = BeautifulSoup(innerHTML, 'lxml')

    links = soup.find('table',{'class':'market-trans'}).find_all("a")
    # print(stock_table)
    # links = stock_table.findAll('a')

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
        mycursor.execute(sql, val)
        mydb.commit()

        print(mycursor.rowcount, "record inserted at " +str(datetime.datetime.now()))

    print("!!!  Done for char "+ i)    
    browser.quit()
##############################
#   END CRAWLING STOCK
##############################
#   START CRAWLING NEWS
##############################
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
        
        sql = "INSERT INTO test_newsblog (date_crawl, date_publish, time_publish, title, author, category) VALUES (%s,%s,%s,%s,%s,%s)"
        val = (dateInsert, tarikh, time, tajuk, penulis, category)
        mycursor.execute(sql, val)
        mydb.commit()

browser.quit()    

##############################
#   END CRAWLING NEWS
##############################
#   START CRAWLING BLOGS
##############################
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

        dateInsert = str(datetime.datetime.now())
        tarikh = a.text
        tajuk = title.text
        penulis = author.text
        category = "blog"
        time = parent_text[5:].strip()

        sql = "INSERT INTO newsblog (date_insert, date_publish, time_publish, title, author, category) VALUES (%s,%s,%s,%s,%s,%s)"
        val = (dateInsert, tarikh, time, tajuk, penulis, category)
        mycursor.execute(sql, val)
        mydb.commit()

    print("!!! END CRAWLING BLOG FOR TODAY")
browser.quit() 


##############################
#   END CRAWLING BLOGS
##############################
#   START CRAWLING QUARTER RESULT
##############################

"""print("!!! START CRAWLING QUARTER RESULT")

browser = webdriver.Firefox(executable_path=r"C:\geckodriver\geckodriver.exe")
print("Open website")
browser.get(urlQuarter)
innerHTML = browser.execute_script('return document.body.innerHTML')
soup = BeautifulSoup(innerHTML, 'lxml')


#to expand the "modify the visible columns i.e. checkboxes"
WebElementexpanded = browser.find_element_by_xpath("//*[@id='ui-accordion-financialResultTableColumnsDiv-header-0']/span")
WebElementexpanded.click()

# to check all check boxes except xCheckBox where x = 1,2,3,4,19,20,22,23
allLinks = browser.find_elements_by_xpath('//input[@type="checkbox"]')
print("Check all checkboxes")
for link in allLinks:
    if link.is_selected() == False:
        link.click()


while True :
    innerHTML = browser.execute_script('return document.body.innerHTML')
    soup = BeautifulSoup(innerHTML, 'lxml')
    elm = browser.find_element_by_class_name('next')        
    table = soup.find("tbody", {"id": "tablebody"}).find_all("tr")

    for row in table:
        value_quarter = []

        for a in row.strings:
            val = value_quarter.append(a)
           
        value_quarter.append(str(datetime.datetime.now()))
        val = tuple(value_quarter)
        print(val)
        sql = "INSERT INTO test_quarter (num, stock, annDate, fy, quarter, hash_val, price, change_val, percents, revenue, pbt, np, nptosh, div_val, net, divpay, npmargin, roe, rps, eps, dps, naps, qoy, yoy, date_insert) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        mycursor.execute(sql, val)
        mydb.commit()

    if 'ui-state-disabled' in elm.get_attribute('class'):
        browser.quit()
        break
        
    elm.click()
    print("Next")"""

##############################
#   END CRAWLING QUARTER RESULT
##############################


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
#   `date_crawl` varchar(255) DEFAULT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

# CREATE TABLE `newsblog` (
#   `date_crawl` varchar(255) DEFAULT NULL,
#   `date_publish` varchar(255) DEFAULT NULL,
#   `time_publish` varchar(255) DEFAULT NULL,
#   `title` text DEFAULT NULL,
#   `author` varchar(255) DEFAULT NULL,
#   `category` varchar(255) DEFAULT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8;


# CREATE TABLE `test_quarter` (
#   `num` varchar(255) DEFAULT NULL,
#   `stock` varchar(255) DEFAULT NULL,
#   `annDate` varchar(255) DEFAULT NULL,
#   `fy` varchar(255) DEFAULT NULL,
#   `quarter` varchar(255) DEFAULT NULL,
#   `hash_val` varchar(255) DEFAULT NULL,
#   `price` varchar(255) DEFAULT NULL,
#   `change_val` varchar(255) DEFAULT NULL,
#   `percents` varchar(255) DEFAULT NULL,
#   `revenue` varchar(255) DEFAULT NULL,
#   `pbt` varchar(255) DEFAULT NULL,
#   `np` varchar(255) DEFAULT NULL,
#   `nptosh` varchar(255) DEFAULT NULL,
#   `div_val` text DEFAULT NULL,
#   `net` varchar(255) DEFAULT NULL,
#   `divpay` varchar(255) DEFAULT NULL,
#   `npmargin` varchar(255) DEFAULT NULL,
#   `roe` varchar(255) DEFAULT NULL,
#   `rps` varchar(255) DEFAULT NULL,
#   `eps` varchar(255) DEFAULT NULL,
#   `dps` varchar(255) DEFAULT NULL,
#   `naps` varchar(255) DEFAULT NULL,
#   `qoy` varchar(255) DEFAULT NULL,
#   `yoy` varchar(255) DEFAULT NULL
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8;