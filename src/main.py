from urllib.request import urlopen
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
import datetime
import pymysql
from os import  path
import  os
import re
from queue import Queue,LifoQueue,PriorityQueue
from blogAuthorCollector import  BlogAuthorCollector

authorList = []
def collectAuthor():
    listPage = "https://www.cnblogs.com/AllBloggers.aspx"
    try:
        html = urlopen(listPage,timeout=5)
        bs = BeautifulSoup(html,'html.parser')
        aList = bs.find_all("a",href = re.compile("https://www\.cnblogs\.com/[a-zA-Z0-9_-]+/$"))
        for author in aList:
            authorUrl = author.attrs["href"]
            authorName = authorUrl[authorUrl.index("/",10)+1:len(authorUrl) - 1]
            authorList.append(authorName)
    except Exception as e:
        print("collectAuthor error:",str(e))
        tracebake.print_exc()
    print("Congraduation!")

if __name__ == '__main__':
    collectAuthor()
    print("collectAuthor ({0}) done!".format(len(authorList)))
    authorList.remove("findumars")
    authorList.remove("JeffreyZhao")
    authorList.remove("lhb25")

    for authorName in authorList:
        try:
            print("{0} started to collect.....".format(authorName))
            authorCollector = BlogAuthorCollector(authorName,'https://www.cnblogs.com')
            authorCollector.startCollect()
        except Exception as e:
            print("Exception:{0}".format(str(e)))
            tracebake.print_exc()
            continue
    authorCollector.dbClose()
    print("Well Done!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
