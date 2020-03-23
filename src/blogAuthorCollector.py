from urllib.request import urlopen
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
from queue import Queue,LifoQueue,PriorityQueue
import datetime
import pymysql
from os import  path
import  os
import re
from baseCollector import BaseCollector

class BlogAuthorCollector(BaseCollector):
    db = pymysql.connect("35.194.142.65", "root", "a23efe65d84acc0c", "blog_mahone_clu")

    def __init__(self,author,rootUrl):
        # osBasePath = "/www/wwwroot/blog.mahone.club/wp-content/imgs"
        # webBasePath = "/wp-content/imgs"
        self.rootUrl = rootUrl
        self.targetLimit = self.rootUrl + "/" + author
        self.target = self.rootUrl + "/" + author
        BaseCollector.__init__(self)

    def getContent(self,bsObj,articleUrl):
        # global downloadMediaList,db
        try:
            baseUrl = self.target[0:articleUrl.index("/", 10)]
            # html = urlopen(articleUrl)
            # bsObj = BeautifulSoup(html, 'html.parser')
            title = bsObj.find("a",{"id":"cb_post_title_url"})
            if title == None:
                postTitle = ""
            else:
                postTitle = title.get_text()
            # print(postTitle)
            contentBody = bsObj.find("div", {"id": "cnblogs_post_body"})
            if contentBody == None:
                return
            imgList = contentBody.find_all("img",{"src":True},src = re.compile("^[hH/]"))
            for img in imgList:
                imgUrl = img.attrs["src"];
                if imgUrl.lower().startswith("http") == False:
                    imgUrl = self.rootUrl + imgUrl
                # imgUrl = getAbsoluteURL(baseUrl,url1 )
                if imgUrl == None:
                    continue
                if imgUrl not in self.downloadMediaList:
                    filePath = self.getDownloadPath(imgUrl, self.osBasePath)
                    if not path.exists(filePath):
                        # print("downloading {0}".format(imgUrl))
                        urlretrieve(imgUrl, self.getDownloadPath(imgUrl, self.osBasePath))
                        self.downloadMediaList.append(imgUrl)
                img.attrs["src"] = self.webBasePath + imgUrl[imgUrl.index("//") + 1:]
            print("post title: {0},tobedone size:{1},done size{2}".format(postTitle,len(self.tobedownArticleList),len(self.downloadContentList)))
            postContent = str(contentBody)
            self.insertContent(postContent,postTitle,1)
        except Exception as e:
            print("getContent error:{0}".format(str(e)))
            tracebake.print_exc()
            # db.close

    def getDownloadPath(self,imgUrl, downloadDirectory):
        if imgUrl.lower().startswith("http") == False:
            imgUrl = self.rootUrl + imgUrl
        path = self.osBasePath + imgUrl[imgUrl.index("//") + 1:]
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        return path

    def getAbsoluteURL(self,baseUrl, source):
        if source.lower().startswith("http") == False:
            abUrl = self.rootUrl + source
        elif source.startswith("data") == True:
            abUrl =  None
        return abUrl

    def insertContent(self,content,title,author):
        sql = "INSERT into wp_1posts(post_content,post_title,post_author,post_date) values(%s,%s,%s,NOW())"
        # print("post sql: {0}".format(sql))
        cursor = self.db.cursor()
        cursor.execute(sql,(content,title,author))
        self.db.commit()
        cursor.close()

    def executeSql(self,sql):
        cursor = self.db.cursor()
        cursor.execute(sql)
        ret = cursor.fetchone()
        return  ret

    def executeNonQuerySql(self, sql):
        cursor = self.db.cursor()
        cursor.execute(sql)

    def dbClose(self):
        self.db.close()

    def collectUrl(self,bsObj):
        # global tobedownArticleQueue,countDone
        articleList = bsObj.find_all("a",href = re.compile("^[hH/]((?!#).)*$"))
        self.countDone += 1
        for article in articleList:
            articleUrl = article.attrs["href"]
            # print(articleUrl,self.targetLimit)
            if articleUrl.startswith(self.targetLimit) and len(articleUrl)>3 \
                    and articleUrl not in self.tobedownArticleList\
                    and articleUrl not in self.downloadContentList:
                # self.tobedownArticleQueue.put(articleUrl)
                self.tobedownArticleList.append(articleUrl)

            # else:
            #     print("discard url:{0}".format(articleUrl))

    def initHometPage(self):
        html = urlopen(self.target,timeout=5)
        self.downloadContentList.append(self.target)
        bsObj = BeautifulSoup(html,'html.parser')
        articleList = bsObj.find_all("a",{"href":True},href = re.compile("^^[hH]ttps://.*(/archive/)|(/category/)|(/tag/).*"))
        for article in articleList:
            articleUrl = article.attrs["href"]
            # print(articleUrl)
            # self.tobedownArticleQueue.put(articleUrl)
            self.tobedownArticleList.append(articleUrl)

    def startCollect(self):
        self.initHometPage()
        # while self.tobedownArticleQueue.qsize() > 0:
        while len(self.tobedownArticleList) > 0:
            try:
                # popOne = self.tobedownArticleQueue.get()
                popOne = self.tobedownArticleList.pop()
                self.downloadContentList.append(popOne)
                # self.tobedownArticleList.remove(popOne)
                print("Pop {0} page start to collect...............".format(popOne))
                html = urlopen(popOne,timeout=5)
                bsObj = BeautifulSoup(html,'html.parser')
                self.collectUrl(bsObj)
                # if countDone > 100:
                #     print("100 pages collected")
                #     break
                self.getContent(bsObj,popOne)
            except Exception as e:
                print("startCollect error:",str(e))
                tracebake.print_exc()
                continue
        # print(self.tobedownArticleList)
        # print(self.downloadContentList)

