import pymysql
from queue import Queue

class BaseCollector():
    osBasePath = "/www/wwwroot/blog.mahone.club/wp-content/imgs"
    webBasePath = "/wp-content/imgs"

    def __init__(self):
        self.countDone = 0
        self.downloadMediaList = []
        self.downloadContentList = []
        self.tobedownArticleList = []
        self.tobedownArticleQueue = Queue()

    def hello(self):
        print("hello")
