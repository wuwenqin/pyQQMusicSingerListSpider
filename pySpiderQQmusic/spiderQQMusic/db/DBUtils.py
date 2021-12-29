# 数据库工具类

import pymysql as pymysql

# 数据库查询用户是否存在
from spiderQQMusic.spider.musicInformationSpider import musicInforSpiderFramInit


def connect_whetherUserExists(user, password):
    # 链接数据库
    db=pymysql.connect(host="localhost",user="root",password="12345678",db="myqqmusicspider")
    cursor=db.cursor()
    sql="select username from user where username='%s' and password='%s'" % (user,password)
    cursor.execute(sql) # 执行查询
    result=cursor.fetchone() # 返回查询结果给result
    db.close() # 关闭数据库
    return result


def insert_IntoUser(username,password,email):
    # 链接数据库
    db = pymysql.connect(host="localhost", user="root", password="12345678", db="myqqmusicspider")
    cursor = db.cursor()
    # 查询用户是否存在
    sql="select username from user where username= '%s'" %username
    cursor.execute(sql)
    result=cursor.fetchone() # 将查询的结果返回给result
    if result:
         return True
    else :
        register_sql="insert into user (username,password,email) values  ('%s','%s','%s')" % (username,password,email)
        cursor.execute(register_sql)
        db.commit()
        print("写入用户数据:",username,password,email)
        db.close()
        return False







