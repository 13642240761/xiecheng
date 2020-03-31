from selenium import webdriver
from bs4 import BeautifulSoup
import time

import MySQLdb

class MySpider:
    def open(self):
        self.con = MySQLdb.connect(host="127.0.0.1", port=3306, user='root', password="19980507",
                                   db="lvyou", charset='utf8')
        self.cursor = self.con.cursor()
        sql = "create table lvyou (title varchar(512),price varchar(16),destination varchar(512),feature text)"
        try:
            self.cursor.execute(sql)
        except:
            self.cursor.execute("delete from lvyou")

        self.baseUrl = "https://huodong.ctrip.com/activity/search/?keyword=%25e9%25a6%2599%25e6%25b8%25af"
        self.chrome = webdriver.Chrome()
        self.count = 0
        self.page = 0
        self.pageCount = 0

    def close(self):
        self.con.commit()
        self.con.close()

    def insert(self, title, price, destination, feature):
        sql = "insert into lvyou (title,price,destination,feature) values (%s,%s,%s,%s)"
        self.cursor.execute(sql, [title, price, destination, feature])

    def show(self):
        self.con = MySQLdb.connect(host="127.0.0.1", port=3306, user='root', password="19980507",
                                   db="lvyou", charset='utf8')
        self.cursor = self.con.cursor()
        self.cursor.execute("select title,price,destination,feature from lvyou")
        rows = self.cursor.fetchall()
        i=1
        for row in rows:
            print(i,row)
            i+=1
        print("Total:",len(rows))
        self.con.close()

    def spider(self, url):
        try:
            self.page += 1
            print("\nPage", self.page, url)
            self.chrome.get(url)
            time.sleep(3)
            html = self.chrome.page_source
            root = BeautifulSoup(html, "lxml")
            div = root.find("div", attrs={"id": "xy_list"})
            divs = div.find_all("div", recursive=False)

            for i in range(len(divs)):
                title = divs[i].find("h2").text
                price = divs[i].find("span", attrs={"class": "base_price"}).text
                destination = divs[i].find("p", attrs={"class": "product_destination"}).find("span").text
                feature = divs[i].find("p", attrs={"class": "product_feature"}).text

                print(title, '\n预付:', price, "\n", destination, feature)

                if self.page == 1:
                    link = root.find("div", attrs={"class": "pkg_page basefix"}).find_all("a")[-2]
                    self.pageCount = int(link.text)
                    print(self.pageCount)

                if self.page < self.pageCount:
                    url = self.baseUrl + "&filters=p" + str(self.page + 1)
                    self.spider(url)

                self.insert(title, price, destination, feature)

        except Exception as err:
            print(err)

    def process(self):
        url = "https://huodong.ctrip.com/activity/search/?keyword=%25e9%25a6%2599%25e6%25b8%25af"
        self.open()
        self.spider(url)
        self.close()


'''
spider = MySpider()
spider.open()
spider.spider("https://huodong.ctrip.com/activity/search/?keyword=%25e9%25a6%2599%25e6%25b8%25af")
spider.close()
'''
spider = MySpider()

while True:
    print("1.爬取")
    print("2.显示")
    print("3.退出")
    s = input("请选择(1,2,3):")

    if s == "1":
        print("Start.....")
        spider.process()
        print("Finished......")
    elif s == "2":
        spider.show()
    else:
        break
