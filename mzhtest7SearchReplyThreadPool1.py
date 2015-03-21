# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 18:15:48 2015
可以爬到所有无需登录的模块
本模块实现了民主湖的若干模块的回复内容的爬取，可以找到你想要的人的帖子及回复内容。
输入参数：
        用户ID
        用户注册时间：需要登录查看
@author: KyleHuang
@Address： Chongqing University
"""
import re  
import urllib2
import datetime
import time
import Queue, threading, sys   
from threading import Thread   
import time,urllib   
# working thread   
class Worker(Thread):   
   worker_count = 0   
   def __init__( self, workQueue, resultQueue, timeout = 0, **kwds):   
       Thread.__init__( self, **kwds )   
       self.id = Worker.worker_count   
       Worker.worker_count += 1   
       self.setDaemon( True )   
       self.workQueue = workQueue   
       self.resultQueue = resultQueue   
       self.timeout = timeout   
       self.start( )   
   def run( self ):   
       ''' the get-some-work, do-some-work main loop of worker threads '''   
       while True:   
           try:   
               callable, args, kwds = self.workQueue.get(timeout=self.timeout)   
               res = callable(*args, **kwds)   
               #print "worker[%2d]: %s" % (self.id, str(res) )   
               self.resultQueue.put( res )   
           except Queue.Empty:   
               break   
           except :   
               print 'worker[%2d]' % self.id, sys.exc_info()[:2]   
                  
class WorkerManager:   
   def __init__( self, num_of_workers=10, timeout = 1):   
       self.workQueue = Queue.Queue()   
       self.resultQueue = Queue.Queue()   
       self.workers = []   
       self.timeout = timeout   
       self._recruitThreads( num_of_workers )   
   def _recruitThreads( self, num_of_workers ):   
       for i in range( num_of_workers ):   
           worker = Worker( self.workQueue, self.resultQueue, self.timeout )   
           self.workers.append(worker)   
           print 'add a task'
   def wait_for_complete( self):   
       # ...then, wait for each of them to terminate:   
       while len(self.workers):   
           worker = self.workers.pop()   
           worker.join( )   
           if worker.isAlive() and not self.workQueue.empty():   
               self.workers.append( worker )   
       #print "All jobs are are completed."   
   def add_job( self, callable, *args, **kwds ):   
       self.workQueue.put( (callable, args, kwds) ) 
       print 'Add a task!'
   def get_result( self, *args, **kwds ):   
       return self.resultQueue.get( *args, **kwds )  
   

def findAuthorArticleWithoutLogin(authorId,date1):

    FidList={280:u'计算机技术',119:u'学术民主湖',14:u'江风竹雨',27:u'人文社科',63:u'好摄之徒',17:u'书香重大',
              109:u'外语角',83:u'黄桷树下',123:u'鱼食天下',107:u'鱼游天下',30:u'激情天下',181:u'数码广场',
             18:u'轻松一刻',92:u'老乡会所',195:u'健康大家谈',100:u'心语新缘',
             #234:u'曝光台',
             #103:u'张贴栏',
             #138:u'生物学院'
             #203:u'租房',218:u'兼职',180:u'民主湖超市'
             }
     #IterateList(authorId,100,FidList[100],date1)
    wm = WorkerManager(15)   
    for fid in FidList:
       wm.add_job( IterateList, authorId,fid,FidList[fid],date1 )   
    wm.wait_for_complete()   #等待工作完成
def IterateList(authorId,Fid,FidName,date1):
    ###该函数主要用来遍历页
     pageStart=1#从第一页访问
     pageEnd=200#最多访问00页，结束
     urlstr='http://www.cqumzh.cn/bbs/forumdisplay.php?fid='+str(Fid);
     #matchstr='space.php?uid='+str(authorId)
     for i in range(pageStart,pageEnd):
         print FidName+u',爬虫爬到第'+str(i)+u'页'
         #合成URL路径
         urlstr2=urlstr+'&page='+str(i)
         #模拟请求网址
         request = urllib2.Request(urlstr2)
         request.add_header('User-Agent', 'fake-client')
         response = urllib2.urlopen(request)
         myPage =response.read()
         #print myPage
         #myItems=re.findall(u'<a title=".*?(\d{4}.*?)"href="(.*?)"',myPage,re.S)  
         myItems=re.findall('<a title=".*?(\d{4}.*?)"href="(.*?)".*?>(.*?)</a></span>.*?<td align="center" style="overflow:hidden"nowrap="nowrap">\r\n<cite>\r\n<a href="(.*?)">(.*?)</a>',myPage,re.S)         
         #myItems各项目说明
         #0:时间
         #1:帖子详细地址
         #2:帖子标题
         #3:作者ID
         
         for item in myItems:    
              GetAuthorArticleAndReplyContent(item[1],authorId,item[2],FidName,i)
             
         #截断时间判断
         length=len(myItems)
         date2=getItemPage(myItems[length-1][0])
         #print date2
         dderror=date2-date1
         if dderror.days<0:
             return
def GetAuthorArticleAndReplyContent(urlshort,authourId,belongTopic,Fidname,pagenumber):
    #在当前页面查找与输入作者ID相关的帖子并记录下来，一个帖子下面所有的
    #belongtTopic：为当前页面的主题帖
    urlstr='http://www.cqumzh.cn/bbs/'+urlshort;
    request = urllib2.Request(urlstr)
    request.add_header('User-Agent', 'fake-client')
    response = urllib2.urlopen(request)
    myPage =response.read()
    #print myPage
         #匹配目标内容
    myItems=re.findall('<a href="space.php\?uid=(\d*)" target="_blank">(.*?)<td class="postauthor".*?</td>',myPage,re.S)
    for item in myItems:
        if item[0]==str(authourId): #找到相同的作者，提前作者的内容，
            st=item[1]
            fItems=re.findall('<table cellspacing="0" cellpadding="0">(.*?)</table>',st,re.S);
            #fItems=re.findall('[\u4e00-\u9fa5]',st,re.S);
            print belongTopic+u'-----回复内容'
            print fItems[0];    
            if mutex.acquire(1): 
                 
                    f.writelines('***************************************************************************************************\n\r')
                    f.writelines(str(Fidname)+u',第'+str(pagenumber)+u'页，'+str(belongTopic)+u',中发表或回复了,\n\r'+str(urlstr)+'\n\r'+fItems[0]+'\n\r')
                    mutex.release()
def getWebAdress(objStr):
             addr=re.findall('.*?href="(.*?)"',objStr,re.S)
             return addr[0]
def getItemPage(objStr):
    mItems=re.findall('\d{4}-\d{1,2}-\d{1,2}',objStr,re.S)
    mdate=datetime.datetime.strptime(str(mItems[0]), "%Y-%m-%d")
    return mdate
if __name__=="__main__":
    #此处输入搜索需要的信息
    authorId=raw_input(u'请输入作者ID：');
    registerDate =raw_input(u'请输入开始日期，（作者注册时间），格式:xxxx-xx-xx');
    dd=datetime.datetime.strptime(registerDate, "%Y-%m-%d")
    print u"爬虫开始爬民主湖了 ......"
    mutex=threading.Lock()
    f = open('Cid'+str(authorId)+'.txt','w+')  
    f.writelines(u"作者"+str(authorId)+u"\n\r") 
    findAuthorArticleWithoutLogin(authorId,dd)
    f.close()