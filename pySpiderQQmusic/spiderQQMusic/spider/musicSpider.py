import time
from concurrent.futures import ThreadPoolExecutor

import openpyxl as openpyxl
import pymysql
from selenium import webdriver
from selenium.webdriver.common.by import By
from lxml import etree
import requests

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36 SLBrowser/6.0.1.9171"
}

dataList=[] # 数据存储数组

def RollDown(web):
    js= "window.scrollTo(0,document.body.scrollHeight)"
    web.execute_script(js)
    time.sleep(1)

# 保存到表格中
def saveExcel(datalist,savepath,keyword):
    filename="QQ音乐__"+keyword+".xlsx"
    savepath=savepath+"/"+filename
    outwb=openpyxl.Workbook()
    outws=outwb.create_sheet(index=0)
    # 表头singer,briefIntroduction,songName,album,albumLink,totalTime
    header=['歌手','简介','歌名','歌曲专辑','专辑链接','歌曲时长']
    datalist.insert(0,header)
    for row in datalist:
        outws.append(row)
    outwb.save(savepath)


# key 关键字 num数量 choice 选择(全部，内地，港台，欧美，日本，韩国) dirname 保存路径, nb_jobs 线程数量
def musicSpiderTogetInformation(key, choice, dirname, nb_jobs):
    index=ord(key)-64
    area=None
    if choice=="全部":
        area=-100
    elif choice == "内地":
        area=200
    elif choice=="港台":
        area = 2
    elif choice=="欧美":
        area=5
    elif choice=="日本":
        area=4
    elif choice=="韩国":
        area=3
    # 拼接地址
    url="https://y.qq.com/n/ryqq/singer_list?index=%d"%index+"&genre=-100&sex=-100&area=%d"%area
    print(url)
    # 使用selenium进行模拟，爬取数据
    option = webdriver.ChromeOptions()
    option.add_argument('--ignore-certificate-errors')
    option.add_argument('-ignore -ssl-errors')
    option.add_experimental_option("detach", True)
    web = webdriver.Chrome(options=option)  # 全屏,记得要在Chrome(options=option)后面，通常我们都是web.Chrome,当时因为这里需要解决强制关闭问题，所以这里要编程option = webdriver.ChromeOptions()，option.add_experimental_option("detach", True)，web = Chrome(options=option)，当时由于又要弄成全屏，所以又要变成web = webdriver.Chrome(options=option)，web.maximize_window()
    web.maximize_window()
    web.implicitly_wait(10)
    web.get(url)
    time.sleep(2)
    # 滚动两次，让数据加载
    RollDown(web)
    RollDown(web)
    time.sleep(1)
    singerlist=[]  # 歌手列表
    ulList=web.find_elements(By.XPATH,'//*[@class="singer_list_txt__item"]')
    for u in ulList:
        href=u.find_element_by_class_name("singer_list_txt__link").get_attribute("href")
        singerlist.append(href)
        print(href)
    #线程池
    pool = ThreadPoolExecutor(max_workers=nb_jobs)
    for url in singerlist:
        if nb_jobs<2:
            details(url)
        else:
            pool.submit(details,url)
    pool.shutdown(wait=True)
    writeIntoDataBase(dataList)
    saveExcel(dataList, dirname, key)
    return len(dataList)

# 一首歌的作者，歌名，简介，专辑等，并将数据写入数据库中以及下载到指定位置
def details(url):
    data=[]
    response = requests.get(url=url, headers=headers).text
    rtree = etree.HTML(response)

    singer = rtree.xpath('//*[@class="data__name_txt"]/text()')[0]  # 歌手
    singer=str(singer)
    briefIntroduction = rtree.xpath('//*[@class="data__desc_txt"]/text()')  # 简介
    if briefIntroduction:
        briefIntroduction = str(briefIntroduction[0])
    else:
        briefIntroduction = str(" ")
    ulList = rtree.xpath('//*[@class="songlist__list"]/li')  # 歌曲列表
    for ul in ulList:
        songName = ul.xpath('.//*[@class="songlist__songname_txt"]/a/@title')[0]  # 歌曲名
        print(songName)
        album = ul.xpath('.//*[@class="songlist__album"]/a/text()')  # 专辑
        if album:
            album = str(album[0])
        else:
            album = str("")
        Link = ul.xpath('.//*[@class="songlist__album"]/a/@href')  # 专辑列表，需要拼接
        if Link:
            Link = str(Link[0])
            albumLink = "https://y.qq.com/" + Link
        else:
            Link = str("")
            albumLink = str("")
        totalTime = ul.xpath('.//*[@class="songlist__time"]/text()')  # 总时间
        if totalTime:
            totalTime = str(totalTime[0])
        else:
            totalTime = str("")
        data.append(singer)
        data.append(briefIntroduction)
        data.append(songName)
        data.append(album)
        data.append(albumLink)
        data.append(totalTime)
        dataList.append(data)


# 写入数据库
def writeIntoDataBase(datalist):
    db=pymysql.connect(host="localhost",user="root",password="12345678",db="myqqmusicspider")
    cursor=db.cursor()
    for data in datalist:
        sql="insert into qqmusicdata (singer,briefIntroduction,songName,album,albumLink,totalTime) values ('%s','%s','%s','%s','%s','%s')" %(pymysql.converters.escape_string(data[0]),pymysql.converters.escape_string(data[1]),pymysql.converters.escape_string(data[2]),pymysql.converters.escape_string(data[3]),pymysql.converters.escape_string(data[4]),pymysql.converters.escape_string(data[5]) )
        cursor.execute(sql)
    db.commit()
    db.close()


if __name__ == '__main__':
    # musicSpiderTogetInformation("B","欧美","./",5)
    url="https://y.qq.com/n/ryqq/singer_list?index=1&genre=-100&sex=-100&area=-100"
    musicSpiderTogetInformation("A","全部","./",10)


