# -*- coding: UTF-8 -*-
'''
Created on 2016-06-04
@author: linghb
'''
import urllib2
import re
import time
import MySQLdb
from collections import deque
import threading

'''
获取html内容
'''
def getHtml(url):
    header={
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection":"keep-alive",
    "Cookie":"_T_WM=3599f463876f0a7ff2617902631127b5; gsid_CTandWM=4uVsCpOz5p5Lf08csDUHJayVla4; ALF=1467728453; SUB=_2A256UEUGDeTxGeRL6lUU8y_KyTiIHXVZu2tOrDV6PUJbktBeLXTskW14__ecfwWVLNnKx6oHZpWktQw-9w..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhxflAenb.JHiA0XuydeIj55JpX5o2p5NHD95QESK2NSKepSozXWs4Dqcjdi--Xi-iFi-2Xi--fiKysiK.Ri--fiKyhiK.c; SUHB=08J6icA84-3QFJ; SSOLoginState=1465136470",
    "Host":"weibo.cn",
    #"Referer":"http://weibo.cn/",
    "Upgrade-Insecure-Requests":"1",
    "User-Agent":"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"
    }
    request=urllib2.Request(url,"",header)
    request.set_proxy('60.9.239.38:8888','http')
    try:
        response=urllib2.urlopen(request, timeout=20)
        time.sleep(5)
        return response.read()
    except Exception , e:
        print e
        time.sleep(30)
        try:
            response=urllib2.urlopen(request, timeout=20)
            time.sleep(2)
            return response.read()
        except Exception , e1:
            print e1
            time.sleep(2)
            return ""
    

'''
过滤粉丝大于1500的数据
return: 
'''
def filterHtml(html):
    list = []
    p = re.compile(r'''<table><tr><td valign=.*?</a></td></tr></table>''')
    p_fans = re.compile(r'''粉丝\d*?人''')
    p_fans_num = re.compile(r'''\d+''')
    match_c = p.findall(html)
    for item in match_c:
        match_fans = p_fans.findall(item)  # 粉丝2451857人
        #print match_fans[0]
        fans_num = p_fans_num.findall(match_fans[0])
        if(int(fans_num[0]) < 1500):
            list.append(item)
    
    return list

'''
获取昵称 和 uid
input: <a href="http://weibo.cn/u/5067607858">荣耀honor</a>
'''
def get_name_uid(content):
    tmp = content.split('<a href="http://weibo.cn/u/')
    if(len(tmp) > 2):
        tmp = tmp[1]
    else:
        tmp = content.split('<a href="http://weibo.cn/')[1]
    uid = tmp.split('">')[0]
    nickname = tmp.split('">')[1].split('</a>')[0]
    print "uid: "+uid, " nickname: " +nickname

'''
获取某个uid所有关注者的uids
'''
def get_uid(uid):
    list = []
    url_base = "http://weibo.cn/" + uid + "/follow?page=" #2517531624
    for i in range(1,1000):
        url = url_base + str(i)
        print url
        html = getHtml(url)
        if(html == ""):
            continue
        items = filterHtml(html)
#         for item in items:
#             content = ''
#             p_nouid = re.compile(r'''<a href="http://weibo.cn/.*?</a>''')
#             match_c = p_nouid.findall(item)
#             if(len(match_c)>1):
#                 content = match_c[1]
#                 get_name_uid(content)
        for item in items:
            p_uid = re.compile(r'''uid=\d{10}''')
            match_uid = p_uid.findall(item)
            if(len(match_uid)>0):
                tmp = match_uid[0]
                uid = tmp.split("uid=")[1]
                list.append(uid)
                
        if html.find("下页") == -1:
            break
        
    return list

'''
获取基本信息 和 学习信息
'''
def getInfo(html):
    dict = {"nickname":"", "sex":"", "area":"", "brief":"", "birthday":"", "education":""}
    p_base_info = re.compile(r'''<div class="tip">基本信息</div>.*?</div>''')
    match_base_info = p_base_info.findall(html)
    if len(match_base_info) > 0: 
        base_info = match_base_info[0]
        tmp = base_info.split('''<div class="tip">基本信息</div><div class="c">''')[1]
        tmp_detail = tmp.split('<br/>')
        for detail in tmp_detail:
            item = detail.split(':')
            if(item[0]=='昵称'):
                dict["nickname"] = item[1]
            elif(item[0]=='性别'):
                dict["sex"] = item[1]
            elif(item[0]=='地区'):
                dict["area"] = item[1]
            elif(item[0]=='简介'):
                dict["brief"] = item[1]
            elif(item[0]=='生日'):
                dict["birthday"] = item[1]
    
    p_education = re.compile(r'''<div class="tip">学习经历</div>.*?</div>''')
    match_education = p_education.findall(html)
    if len(match_education) > 0: 
        education = match_education[0]
        tmp = education.split('''<div class="tip">学习经历</div><div class="c">''')[1]
        detail = tmp.replace('&nbsp;',' ').replace('<br/>',';8').replace('</div>','').replace('·','')
        dict["education"] = detail
    
    return dict
    
# if __name__ == '__main__':
#     uid_sheet = deque(["2517531624","##"]) # 操作列表
#     i = 1
#     while(len(uid_sheet) > 0):
#         uid_this = uid_sheet.popleft()
#         print '----第' + str(i) + '轮开始----'
#         if(uid_this == '##'):
#             print '----第' + str(i) + '轮结束----'
#             i = i + 1
#             if(i == 5):
#                 break
#             uid_sheet.append("##")
#             continue
#         uids = get_uid(uid_this)
#         for uid in uids:
#             print uid 
#             count = cursor.execute("select id from user_info where uid = '" + uid + "'")
#             print count
#             if(count == 0):
#                 
#                 url_info = "http://weibo.cn/" + uid + "/info"
#                 html_info = getHtml(url_info)
#                 dict = {"nickname":"", "sex":"", "area":"", "brief":"", "birthday":"", "education":""}
#                 if(html_info != ""):
#                     dict = getInfo(html_info)
#                      
#                 list = (uid,dict["nickname"],dict["sex"],dict["birthday"],dict["area"],dict["education"],dict["brief"],'')
#                 sql = 'insert into user_info(uid,nickname,sex,birthday,area,education,brief,name) values(%s,%s,%s,%s,%s,%s,%s,%s)'
#                 cursor.execute(sql,list)
#                 print 'insert success.'
#             else:
#                 uids.remove(uid)
#             list_rel = (uid_this,uid)
#             sql_rel = 'insert into relationship(uid,uid_follow) values(%s,%s)'
#             cursor.execute(sql_rel,list_rel)
#                         
#             conn.commit()
#             
#             
#         uid_sheet.extend(uids)
#         
#     cursor.close()
#     conn.close()

def dealItem(id):
    conn=MySQLdb.connect(host="localhost",user="root",passwd="xxx",db="weibo",charset="utf8")
    cursor =conn.cursor()
    count = cursor.execute("select uid from user_info where id = " + str(id))
    if(count > 0):
        data = cursor.fetchone()
        uid_this = data[0]
        print "=== id : " + str(id) + " --- " + "uid_this : " + uid_this
        uids = get_uid(uid_this)
        for uid in uids:
            print "----------------\n" + uid 
            count = cursor.execute("select id from user_info where uid = '" + uid + "'")
            print count
            if(count == 0):
                 
                url_info = "http://weibo.cn/" + uid + "/info"
                html_info = getHtml(url_info)
                dict = {"nickname":"", "sex":"", "area":"", "brief":"", "birthday":"", "education":""}
                if(html_info != ""):
                    dict = getInfo(html_info)
                      
                list = (uid,dict["nickname"],dict["sex"],dict["birthday"],dict["area"],dict["education"],dict["brief"],'')
                sql = 'insert into user_info(uid,nickname,sex,birthday,area,education,brief,name) values(%s,%s,%s,%s,%s,%s,%s,%s)'
                cursor.execute(sql,list)
                print 'insert user_info success.'
                conn.commit()
                
            count = cursor.execute("select id from relationship where uid = '" + uid_this + "' and uid_follow = '" + uid + "'")
            if(count == 0):
                list_rel = (uid_this,uid)
                sql_rel = 'insert into relationship(uid,uid_follow) values(%s,%s)'
                cursor.execute(sql_rel,list_rel)
                print 'insert relationship success.'     
                conn.commit()
    cursor.close()
    conn.close()
    
if __name__ == '__main__':
        id = 483
        while True:
            thread = []
            for i in range(3):
                id = id + 1
                t = threading.Thread(target=dealItem,args=(id,))
                t.start()
                thread.append(t)    
            for t in thread:
                t.join() 
        
  