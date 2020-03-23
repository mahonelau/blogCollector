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
    html = urlopen(listPage,timeout=1)
    bs = BeautifulSoup(html,'html.parser')
    aList = bs.find_all("a",href = re.compile("https://www\.cnblogs\.com/[a-zA-Z0-9_-]+/$"))
    for author in aList:
        authorUrl = author.attrs["href"]
        authorName = authorUrl[authorUrl.index("/",10)+1:len(authorUrl) - 1]
        authorList.append(authorName)

def collectAuthorCSDN():
    listPage = "https://blog.csdn.net/rank/writing_rank"
    html = urlopen(listPage)
    bs = BeautifulSoup(html,'html.parser')
    aList = bs.find_all("a",href = re.compile("https://blog\.csdn\.net/[a-zA-Z0-9_-]+.*$"))
    print(aList)
    authorList.clear()
    for author in aList:
        authorUrl = author.attrs["href"]
        authorName = authorUrl[authorUrl.index("/",10)+1:len(authorUrl) - 1]
        authorList.append(authorName)

collectAuthor()
print(authorList)
#
# a = BlogAuthorCollector("findumars","https://www.cnblogs.com")
# a.startCollect()

