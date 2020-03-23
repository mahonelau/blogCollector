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
        html = urlopen(listPage)
        bs = BeautifulSoup(html,'html.parser')
        aList = bs.find_all("a",href = re.compile("https://www\.cnblogs\.com/[a-zA-Z0-9_-]+/$"))
        for author in aList:
            authorUrl = author.attrs["href"]
            authorName = authorUrl[authorUrl.index("/",10)+1:len(authorUrl) - 1]
            authorList.append(authorName)
    except Exception as e:
        print("collectAuthor error:",str(e))
    print("Congraduation!")

if __name__ == '__main__':
    collectAuthor()
    authorList.remove("findumars")
    authorList.remove("JeffreyZhao")
    print(authorList)
    for authorName in authorList:
        try:
            print("{0} started to collect.....".format(authorName))
            authorCollector = BlogAuthorCollector(authorName,'https://www.cnblogs.com')
            authorCollector.startCollect()
        except Exception as e:
            print("Exception:{0}".format(str(e)))
            continue
    print("Well Done!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

# osBasePath = "/www/wwwroot/blog.mahone.club/wp-content/imgs"
# webBasePath = "/wp-content/imgs"
# targetLimit = "https://www.cnblogs.com/skynet"
# target = "https://www.cnblogs.com/skynet"
# countDone = 0
# downloadMediaList = []
# downloadContentList = []
# tobedownArticleList = []
# tobedownArticleQueue = Queue()
#
# db = pymysql.connect("35.194.142.65", "root", "a23efe65d84acc0c", "blog_mahone_clu")

def getContent(bsObj,articleUrl):
    global downloadMediaList,db
    try:
        baseUrl = target[0:articleUrl.index("/", 10)]
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
                imgUrl = baseUrl + imgUrl
            # imgUrl = getAbsoluteURL(baseUrl,url1 )
            if imgUrl == None:
                continue
            if imgUrl not in downloadMediaList:
                filePath = getDownloadPath(imgUrl, osBasePath)
                if not path.exists(filePath):
                    print("downloading {0}".format(imgUrl))
                    urlretrieve(imgUrl, getDownloadPath(imgUrl, osBasePath))
                    downloadMediaList.append(imgUrl)
            img.attrs["src"] = webBasePath + imgUrl[imgUrl.index("//") + 1:]
        print("post title: {0}".format(postTitle))
        postContent = str(contentBody)
        insertContent(postContent,postTitle,1)
        downloadContentList.append(articleUrl)
            #     if not img.attrs["src"].startswith("data"):
            #         print(img.attrs["src"])
            #         imgUrl = img.attrs["src"]
            #         if imgUrl.lower().startswith("http") == False:
            #             imgUrl = curUrl + imgUrl
            #         img.attrs["src"] = webBasePath + imgUrl[imgUrl.index("//")+1:]
            #         downLoadImg(imgUrl)
            # print( bsObj.find("div", {"id":"cnblogs_post_body"}))
    except Exception as e:
        print(e)
        db.commit()
        db.close

def getDownloadPath(imgUrl, downloadDirectory):
    if imgUrl.lower().startswith("http") == False:
        imgUrl = baseUrl + imgUrl
    path = osBasePath + imgUrl[imgUrl.index("//") + 1:]
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return path

def getAbsoluteURL(baseUrl, source):
    if source.lower().startswith("http") == False:
        abUrl = baseUrl + source
    elif source.startswith("data") == True:
        abUrl =  None
    return abUrl

def downLoadImgold(imgUrl):
    img = urlopen(imgUrl)
    fileName = imgUrl[imgUrl.rindex("/")+1:len(imgUrl)]
    fileDir = osBasePath + imgUrl[imgUrl.index("//")+1:imgUrl.rindex("/")]
    if not path.exists(fileDir):
        os.makedirs(fileDir)
    f = open(fileDir + "/" + fileName,'wb')
    f.write(img.read())

def insertContent(content,title,author):
    # sql = "INSERT into wp_1posts(post_content,post_title,post_author,post_date) values("{dbcontent},r"{dbtitle}",{dbauthor},NOW())".format(dbcontent = content,dbtitle = title,dbauthor = author)
    sql = "INSERT into wp_1posts(post_content,post_title,post_author,post_date) values(%s,%s,%s,NOW())"
    # print("post sql: {0}".format(sql))
    cursor = db.cursor()
    cursor.execute(sql,(content,title,author))
    db.commit()
    cursor.close()

def executeSql(sql):
    cursor = db.cursor()
    cursor.execute(sql)
    ret = cursor.fetchone()
    return  ret

def executeNonQuerySql(sql):
    cursor = db.cursor()
    cursor.execute(sql)

def connectDB():
    global db
    db = pymysql.connect("35.194.142.65", "root", "a23efe65d84acc0c", "blog_mahone_clu")
    # cursor = db.cursor()
    # cursor.execute("SELECT VERSION()")


def collectUrl(bsObj):
    global tobedownArticleQueue,countDone
    articleList = bsObj.find_all("a",href = re.compile("^[hH/]((?!#).)*$"))
    countDone += 1
    for article in articleList:
        articleUrl = article.attrs["href"]
        # print(articleUrl)
        if articleUrl.startswith(targetLimit) and len(articleUrl)>3 \
                and articleUrl not in tobedownArticleList\
                and articleUrl not in downloadContentList:
            tobedownArticleQueue.put(articleUrl)
            tobedownArticleList.append(articleUrl)
        # else:
        #     print("discard url:{0}".format(articleUrl))

def init():
    html = urlopen(target)
    downloadContentList.append(target)
    bsObj = BeautifulSoup(html,'html.parser')
    articleList = bsObj.find("a",{"href":True},href = re.compile("^^[hH]ttps://.*(/archive/)|(/category/)|(/tag/).*"))
    for article in articleList:
        articleUrl = article.attrs["href"]
        tobedownArticleQueue.put(articleUrl)
        tobedownArticleList.append(articleUrl)
    print(tobedownArticleList)
def start():
    init()
    while tobedownArticleQueue.qsize() > 0:
        popOne = tobedownArticleQueue.get()
        tobedownArticleList.remove(popOne)
        print("Pop {0}".format(popOne))
        html = urlopen(popOne)
        bsObj = BeautifulSoup(html,'html.parser')
        collectUrl(bsObj)
        if countDone > 100:
            print("100 pages collected")
            break
        getContent(bsObj,popOne)
    db.commit()
    db.close()

