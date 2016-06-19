# -*- coding: utf-8 -*-
'''
Created on 2016-06-04
@author: linghb
'''

import MySQLdb
import spider
from spider import *
import sys
reload(sys)
sys.setdefaultencoding('utf8')

if __name__ == '__main__':
    conn=MySQLdb.connect(host="localhost",user="root",passwd="xxx",db="weibo",charset="utf8")
    cursor =conn.cursor()
    count = cursor.execute("select uid from user_info where nickname = ''")
    data = cursor.fetchall()
    for item in data:
        url = "http://weibo.cn/" + item[0] + "/info"
        print url
        content = getHtml(url)
        if(content!=""):
            dict = {"nickname":"", "sex":"", "area":"", "brief":"", "birthday":"", "education":""}
            dict = getInfo(content)
            print dict
            cursor.execute("update user_info \
            set nickname= '" + dict["nickname"] + "', sex = '" + dict["sex"] + "', birthday = '" + dict["birthday"] +\
             "', area = '" + dict["area"] + "', brief = '" + dict["brief"] + "', education = '" + dict["education"] +\
              "'  where uid = '" + item[0] + "'")
            conn.commit()
            print "insert success!"
       
    cursor.close()
    conn.close()    