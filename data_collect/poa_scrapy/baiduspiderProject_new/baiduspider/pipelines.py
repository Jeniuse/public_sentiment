import time
import json
import os
import datetime
###############################################################################
import happybase
from kafka import KafkaProducer   #引入包，如果你在自己的电脑上跑，得先安装kafka
from oraclepool import OrclPool
import jieba
global producer
class BaiduspiderPipeline(object):
    #打开hbase
    connection = happybase.Connection(host='172.16.54.147', port=16000)  # 得到连接
    connection.open()  # 打开连接
    table = connection.table('CONF_FORUM')  # 根据名字得到表的实例

    urlList = []
    deltaList=[]
    templist = []
    informList = []

    def __init__(self):
        ###############################################################################
        global producer
        # producer = KafkaProducer(bootstrap_servers=['172.16.54.139:6667'])
        producer = KafkaProducer(bootstrap_servers=['172.16.54.139:6667','172.16.54.140:6667','172.16.54.141:6667','172.16.54.148:6667'])
        # 查询关键字
        #取得关键字
        os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
        op =OrclPool()
        sql = "select key_word from BASE_ANALYSIS_SENTIMENT where DICT_ENABLED_VALUE=300010000000001"
        list1 = op.fetch_all(sql)
        keylist = []
        for node in list1:
            temp1 = str(node).replace("'", '')
            temp2 = temp1.replace("(" or ")", "")
            temp3 = temp2.replace(")", "")
            temp4 = temp3.split(",")
            for key in temp4:
                if key != '':
                    keylist.append(key)
        keylist = list(set(keylist))
        with open('keywords.txt','w',encoding= 'utf8') as fp:
            fp.write(json.dumps(keylist,ensure_ascii=False))
        # 自定义分词库---begin
        os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
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

    def process_item(self, item, spider):

        if item["IsFilter"]:
            #记录id并存在urlList
            urlId = item['urlId']
            self.templist.append(urlId)
            # 比对id找到增量，并存入Kafka
            try: #首次添加的异常处理
                if urlId not in self.urlList:
                    self.deltaList.append(urlId)
                    self.informList.append(dict(item))
            except:
                self.deltaList.append(urlId)
                self.informList.append(dict(item))

        return item

    def open_spider(self,spider):
        self.urlList = self.read_file("./jsonfile/%s_UrlList.json"%spider.name)

    def close_spider(self,spider):
        self.urlList = self.templist
        #将数据写入文件
        # self.changeUrlListFile(self.urlList,spider.name)
        #将差值列表存入josn
        # self.write_file("./jsonfile/%s_DeltaList.json"%spider.name,self.deltaList)
        #关闭爬虫时将数据写入消息队列
        self.kafka_input(self.informList,spider.name)

    def write_file(self,path,list):
        self.f = open(path, "w", encoding='UTF-8')
        content = json.dumps(list, ensure_ascii=False)
        self.f.write(content)
        self.f.close()

    def read_file(self,path):
        try:
            self.f = open(path, "r", encoding='UTF-8')  # 读取josn中的上次的链接
            content = json.load(self.f)
            self.f.close()
            return content   # 将数据存入列表
        except:
            self.write_file(path,[])

    def Kafka_fun(self,item,origin):
        ###############################################################################
        global producer
        try:
            pstmt = {'TITLE':'','INTRODUCTION':'','ORIGIN_VALUE':'','ORIGIN_NAME':'','OCCUR_TIME':'','URL':'','CONF_WORD':''}
            pstmt['TITLE']=item['title'][:30]
            pstmt['URL']=item['url']
            pstmt['INTRODUCTION']=item['info'][:350]
            pstmt['OCCUR_TIME']=item['time']
            pstmt['ORIGIN_VALUE']='500010000000001'
            pstmt['ORIGIN_NAME']='论坛'
            pstmt['BROWSE_SIZE']=item['read']
            pstmt['COMMENT_SIZE']=item['comment']
            pstmt['FETCH_TIME']=item['spidertime']
            pstmt['LAST_UPDATE_TIME']=item['latestcomtime']
            pstmt['THUMBSUP_SIZE'] = None
            # 分词---begin
            se = '%s。%s'%(item['title'],item['info']) # 得到标题和内容
            res_part = jieba.lcut_for_search(se) # 分词后返回list
            participle = set(res_part) # 去重
            sepa = '$$'
            conf_word = sepa.join(participle) # conf_word为拼接后的字符串
            pstmt['CONF_WORD']=conf_word
            # 分词---end
            msg = json.dumps(pstmt,ensure_ascii=False)
            print('========================================')
            print(msg)
            producer.send('postsarticles', msg.encode('utf-8'))
            # Hbase--begin
            item['conf_word'] = conf_word
            self.HbaseTranport(item)
            #Hbase--end
        except Exception as e:
            self.export_log({"type":"producer","data":pstmt,"exception":str(e)})

    def export_log(self,log_info):
        log_time = time.strftime("%Y-%m-%d", time.localtime())
        log_time1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if not os.path.exists('/tmp/log/log_poa/'):
            os.makedirs('/tmp/log/log_poa/')
        with open('/tmp/log/log_poa/kafka-%s.log'%log_time,'a+') as fp:
            fp.write('%s:%s'%(log_time1,json.dumps(log_info,ensure_ascii=False)))
            fp.write('\n')

    def kafka_input(self,infoList,origin):
        if len(infoList) != 0:
            for info in infoList:
                self.Kafka_fun(info, origin)
        else:
            print("列表为空")

    def changeUrlListFile(self,newlist,spiderName):
        fileList = self.read_file("./jsonfile/%s_UrlList.json"%spiderName)
        # 追加去重
        fileList.extend(newlist)
        fileList = list(set(fileList))
        if len(fileList)>1000:
            fileList = fileList[:200]
        self.write_file("./jsonfile/"+spiderName+"_UrlList.json", fileList)

    def HbaseTranport(self, item):
        if item['time'].count('-') == 1:
            item['time'] = item['time'] + '-1 00:00:00'
        if item['time'].count(':') == 0:
            item['time'] = item['time'] + ' 00:00:00'
        data = {'FAMILY:CRAWL_TIME': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'FAMILY:PUBLISH_TIME': item['time'],
                'FAMILY:TITLE': json.dumps(item['title'][:50]),
                'FAMILY:CONTENT': json.dumps(item['info'][:400]),
                'FAMILY:KEY_WORDS': json.dumps(item['conf_word'])
                }
        self.table.put(row=item['url'], data=data)  # 向表中传入数据