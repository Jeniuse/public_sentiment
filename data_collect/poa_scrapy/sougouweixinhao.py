# -*- coding: utf-8 -*-

import wechatsogou
import requests
import random
import time
import json
from bs4 import BeautifulSoup
from kafka import KafkaProducer
import os
from oraclepool import OrclPool
import jieba
import datetime
import happybase
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
global producer
producer = KafkaProducer(bootstrap_servers=['172.16.54.139:6667','172.16.54.140:6667','172.16.54.141:6667','172.16.54.148:6667'])

# 检测ip是否失效
def check_ip(ips):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'
    }
    # 以下测试IP
    try:
        requests.get("http://www.baidu.com", headers=headers, proxies=ips, timeout=2)  # 测试用网站
        print('time sleep 2s.......................')
        time.sleep(2)
    except Exception as e:
        print("Ip Invalid:",e)
        usefulIPlist = read_Proxies()[1:]
        writeProxies(usefulIPlist)

# 检测ip是否失效
def check_ip_list(ip_list):
    print('===================check ip===================')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'
    }
    # 以下测试IP
    usefulIPlist = []
    for ip in ip_list:
        try:
            requests.get("http://www.baidu.com", headers=headers, proxies=ip, timeout=2)  # 测试用网站
            print(ip)
            usefulIPlist.append(ip)
        except Exception as e:
            print(e)
    writeProxies(usefulIPlist)

# 获取免费代理
def get_ip_free():
    print('===================get free_ip===================')
    time.sleep(180)
    """ 从代理网站上获取代理"""
    url = 'http://www.xicidaili.com/wt'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'
    }
    ip_list = []
    try:
        page = requests.get(url, headers=headers,timeout=5)
    except Exception as e:
        print("require ip failed:",e)
        return False
    soup = BeautifulSoup(page.text, 'lxml')
    ul_list = soup.find_all('tr', limit=15)  # limit=30
    print("IP POOL ip length:%d"%len(ul_list))
    for i in range(2, len(ul_list)):
        line = ul_list[i].find_all('td')
        ip = line[1].text
        port = line[2].text
        address = ip + ':' + port
        proxy = get_proxy(address)
        ip_list.append(proxy)
    # 以下测试IP
    usefulIPlist = []
    for ip in ip_list:
        try:
            page = requests.get("http://www.baidu.com", headers=headers, proxies=ip, timeout=2)  # 测试用网站
            print("Ip validable")
            usefulIPlist.append(ip)
        except:
            print("Ip not validable")
    if (len(usefulIPlist) == 0):
        print("get ip failed")
        get_ip_free()
    else:
        print("IP POOL ip length:%d"%len(usefulIPlist))
        ratio = len(usefulIPlist)/15
        print('==========================ip validable percent:%s'%str(ratio))
        writeProxies(usefulIPlist)
    return True

# 获取付费代理
def get_ip():
    """ 从代理网站上获取代理"""
    print('===================get pay agent ip===================')
    url = 'http://webapi.http.zhimacangku.com/getip?num=5&type=1&pro=&city=0&yys=0&port=1&pack=37981&ts=0&ys=0&cs=0&lb=1&sb=0&pb=5&mr=2&regions='
    url = 'http://webapi.http.zhimacangku.com/getip?num=3&type=2&pro=&city=0&yys=0&port=1&pack=67333&ts=0&ys=0&cs=0&lb=1&sb=0&pb=45&mr=1&regions='
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'
    }
    ip_list = []
    try:
        zm_resp = requests.get(url,timeout=5)
        ip_json = json.loads(zm_resp.text)
        ip_data = ip_json['data']
        if ip_json['code'] != 0:
            print('===================pay agent ip===================')
            print(ip_json['data'])
            print(ip_json['msg'])
            free_res = get_ip_free()
            if free_res == True:
                return True
            else:
                return False
        if len(ip_json)==1:
            print('===================pay agent ip upper limit has been reached===================')
            print(ip_json[0])
            free_res = get_ip_free()
            if free_res == True:
                return True
            else:
                return False
    except requests.exceptions.ConnectionError as e:
        print('can not access')
        print(e)
        free_res = get_ip_free()
        if free_res == True:
            return True
        else:
            return False
    except Exception as e:
        print("require ip failed:",e)
        get_ip()
        return False
    print("IP POOL ip length:%d"%(len(ip_data)-1))
    for ip in ip_data:
        if ip != "":
            proxy = get_proxy("%s:%s"%(ip['ip'], ip['port']))
            ip_list.append(proxy)
    # 以下测试IP
    usefulIPlist = []
    print(ip_list)
    for ip in ip_list:
        try:
            page = requests.get("http://www.baidu.com", headers=headers, proxies=ip, timeout=2)  # 测试用网站
            print("ip validable:%s"%ip)
            usefulIPlist.append(ip)
        except Exception as e:
            print("Ip not validable:",e)
    if (len(usefulIPlist) == 0):
        print("get ip failed,reget")
        get_ip()
    else:
        print("valid ip length:%d"%len(usefulIPlist))
        ratio = len(usefulIPlist)/5
        print('==========================ip validable percent:%s'%str(ratio))
        writeProxies(usefulIPlist)
    return True

def get_proxy(aip):
    """构建格式化的单个proxies"""
    proxy_ip = 'http://' + aip
    proxy_ips = 'https://' + aip
    proxy = {"http": proxy_ip, "https": proxy_ips}
    return proxy

def writeProxies(proxies):
    f = open("proxies.json", "w", encoding='UTF-8')
    content = json.dumps(proxies, ensure_ascii=False)
    f.write(content)
    print("write IP finish")
    f.close()

def read_Proxies():
    try:
        f = open('proxies.json', "r", encoding='UTF-8')  # 读取josn中的上次的链接
        return json.load(f)  # 将数据存入列表
    except Exception as e:
        print("file not found")
        print(e)
        return []

def get_data(listDic,gzh):
    print("get article list length:" + str(len(listDic)))
    itemList = []
    for art in listDic:
        article = art['article']
        wechat_name = art['gzh']['wechat_name']
        url = article['url']
        if wechat_name == gzh:
            localtime = time.localtime(article['time'])
            t = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
            dic = {
                'title': article['title'],
                'info': article['abstract'],
                # 'info': article['info'],
                'time': t,
                'url': article['url']
            }
            itemList.append(dic)
    return itemList


def get_article(gzh,titleList):
    articleList = []
    deltaList = []
    maxConut = 3
    keyword = gzh
    count = 0
    isSuccess = False
    page = 1
    while(1):
        iplist = read_Proxies()
        print('read ip============================================')
        for ip in iplist:
            try:
                # captcha_break_time:验证码重输次数
                ws_api = wechatsogou.WechatSogouAPI(proxies=ip, timeout=10, captcha_break_time=2)
                itemList = []
                while(page<=10):
                    print('scrapy====%s====article==========page %d'%(gzh, page))
                    time.sleep(10)
                    itemList = get_data(ws_api.search_article(keyword, page=page), gzh)  # 得到数据，并转换数据
                    page = page+1
                    print("\nreturn article list length:" + str(len(itemList)))
                    for art in itemList:
                        print(art['title'])
                        unique = art['title'] + '/' + art['time']
                        articleList.append(unique)
                        if unique not in titleList:
                            # 增量,在此处存入消息队列
                            print('kafka')
                            Kafka_fun(art)
                            deltaList.append(art['title'])
                print("next article list")
                isSuccess = True
                break
            except Exception as e:
                print("read article error,check ip is validable?")
                print(e)
                check_ip(ip)
                continue
        if (isSuccess == False):
            count = count + 1
            if (count > maxConut):
                print("OK，article locked！")  # 封锁后直接返回已爬取的
                return False
            else:
                get_ip()  # 得到代理IP列表
                continue
        else:
            break
    print("Finish")
    return articleList

def run():
    global producer
    # 自定义分词库---begin
    op = OrclPool()
    sql = 'select WORD from CONF_WORD'
    lex_list = op.fetch_all(sql)
    lex_str = '$$$$$'
    for lex in lex_list:
        lex_str = '%s\n%s'%(lex_str,lex[0])
    with open('userdict.txt','w',encoding= 'utf8') as fp:
        fp.write(lex_str)
    jieba.load_userdict('userdict.txt')
    # 自定义分词库---end
    print('==================begin==================')
    ip_list = read_Proxies()
    if len(ip_list)==0:
        if (get_ip() == False):
            print("can not get IP")
            return
    else:
        check_ip_list(ip_list)

    # testlist = [{'title': '1', 'info': '11', 'time': '1', 'url': '1'},  # 测试用数据
    #             {'title': '2', 'info': '22', 'time': '1', 'url': '1'},]
    gzhList = ['户户通315行业网站','户户通微平台','户户通行业服务中心','户户通中九卫星用户交流平台','广播电视信息']
    count_art = 0

    title_list = []  # 最终的文章列表
    pageCount = 0
    for gzh in gzhList:
        print(gzh)
        pageCount = pageCount+1
        # 处理公众号
        # 首次出错处理
        try:
            titleList_key = read_file("./baiduspiderProject_new/baiduspider/jsonfile/sougou.json")[gzh]
        except:
            titleList_key = []
        #获得公众号文章
        print('scrapy weixin====%s====article'%(gzh))
        article_list = get_article(gzh,titleList_key)
        if(article_list==False):
            print('failed time sleep 5s=============================================')
            time.sleep(5)#失败停止5s
            continue
        else:
            title_list = article_list
        time.sleep(20)

    # 字典记录数据
    tempdic = read_dic("./baiduspiderProject_new/baiduspider/jsonfile/sougou.json")
    tempdic.update({gzh: title_list})
    write_file("./baiduspiderProject_new/baiduspider/jsonfile/sougou.json", tempdic)
    print('==================end==================')

def write_file(path, list):
    f = open(path, "w", encoding='UTF-8')
    content = json.dumps(list, ensure_ascii=False)
    f.write(content)
    f.close()
def read_dic(path):
    try:
        f = open(path, "r", encoding='UTF-8')  # 读取josn中的上次的链接
        return json.load(f)  # 将数据存入列表
    except:
        return {}

def read_file(path):
    try:
        f = open(path, "r", encoding='UTF-8')  # 读取josn中的上次的链接
        return json.load(f)  # 将数据存入列表
    except:
        return []

def Kafka_fun(art):
    global producer
    pstmt = {'TITLE': '', 'INTRODUCTION': '', 'ORIGIN_VALUE': '', 'ORIGIN_NAME': '', 'OCCUR_TIME': '', 'URL': '', 'BROWSE_SIZE':'', 'COMMENT_SIZE':'', 'FETCH_TIME':'', 'LAST_UPDATE_TIME':'', 'THUMBSUP_SIZE':'', 'CONF_WORD': ''}
    pstmt['TITLE'] = art['title'][:30]
    pstmt['URL'] = art['url']
    pstmt['INTRODUCTION'] = art['info'][:350]
    pstmt['OCCUR_TIME'] = art['time']
    pstmt['ORIGIN_VALUE'] = '500010000000002'
    pstmt['ORIGIN_NAME'] = '微信'
    pstmt['BROWSE_SIZE'] = None
    pstmt['COMMENT_SIZE'] = None
    pstmt['FETCH_TIME'] = None
    pstmt['LAST_UPDATE_TIME'] = None
    pstmt['THUMBSUP_SIZE'] = None
    # 分词---begin
    se = '%s。%s'%(art['title'],art['info']) # 得到标题和内容
    res_part = jieba.lcut_for_search(se) # 分词后返回list
    participle = set(res_part) # 去重
    sepa = '$$'
    conf_word = sepa.join(participle) # conf_word为拼接后的字符串
    pstmt['CONF_WORD']=conf_word
    # 分词---end
    # hbase---start
    if art['time'].count('-') == 1:
        art['time'] = art['time'] + '-1 00:00:00'
    if art['time'].count(':') == 0:
        art['time'] = art['time'] + ' 00:00:00'
    data = {'FAMILY:CRAWL_TIME': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'FAMILY:PUBLISH_TIME': art['time'],
            'FAMILY:TITLE': json.dumps(art['title'][:50]),
            'FAMILY:CONTENT': json.dumps(art['info'][:400]),
            'FAMILY:KEY_WORDS': json.dumps(conf_word)
            }
    try:
        table.put(row=art['url'], data=data)  # 向表中传入数据
    except Exception as e:
        print("hbase:%s"%str(e))
    # hbase---end
    msg = json.dumps(pstmt, ensure_ascii=False)
    print("------------------------------------------------------------------------------------")
    print(msg)
    print("------------------------------------------------------------------------------------")
    try:
        producer.send('postsarticles', msg.encode('utf-8'))
    except Exception as e:
        print("kafka:%s"%str(e))


# 以下为运行所用代码
#打开hbase
connection = happybase.Connection(host='172.16.54.147', port=16000)  # 得到连接
connection.open()  # 打开连接
table = connection.table('CONF_FORUM')  # 根据名字得到表的实例
run()
