# -*- coding: utf-8 -*- 
from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json
import time
import os
import py4j
# import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

# 获取关键字
def update_keywords_fromtxt():
	keywords = {}
	with open('../keywords.txt','r') as fp:
		keywords = json.loads(fp.read())
	return keywords

# 批量插入数据库
def basd_info_add(sql):
	try:
		with open('insert_basd_sql.txt','w',encoding= 'utf8') as fp:
			fp.write(sql)
		os.system('python3 insert_basd.py > sql_check.txt')
		print('插入数据库')
		# print(sql)
	except Exception as e:
		if sql != 'insert all select 1 from dual':
			export_log({"type":"批量插入sql","data":sql,"exception":str(e)})

# SQL拼接
def sendPartition(iter):
	sql = 'insert all '
	b = False
	for record in iter:
		try:
			b = True
			# 拼接内容部分的sql
			sql_content = ""
			res = json.loads(record[0])
			split_len = len(res['OCCUR_TIME'].split('-'))-1 # 时间-的个数
			occur_time = res['OCCUR_TIME']
			# 时间处理
			if len(occur_time)<15:
				if split_len==1:
					occur_time = "%s-01 00:00:00"%occur_time
				elif split_len==2:
					occur_time = "%s 00:00:00"%occur_time
				else:
					occur_time = "%s-01-01 00:00:00"%occur_time
			else:
				occur_time = "%s"%res['OCCUR_TIME']
			try:
				time.strptime(occur_time,"%Y-%m-%d %H:%M:%S")
			except:
				export_log({"type":"时间处理错误","data":res})
				occur_time = "2000-01-01 00:00:00"
			# 简介为空的情况
			if res['INTRODUCTION'] != '':
				res['TITLE'] = res['TITLE'].replace('\'','"')
				res['INTRODUCTION'] = res['INTRODUCTION'].replace('\'','"')
				sql_content = ",'"+res['TITLE']+"','"+res['INTRODUCTION']+"','"+res['URL']+"',to_timestamp('"+occur_time+"','yyyy-mm--dd hh24:mi:ss.ff'),"+res['ORIGIN_VALUE']+",'"+res['ORIGIN_NAME']+"') "
			else:
				if res['ORIGIN_VALUE'] == '500010000000002':
					export_log({"type":"没有简介","data":res})
				else:
					export_log({"type":"没有阅读权限","data":res})
			if sql_content != "":
				# 拼接内容的sql，拼接关键字
				sql_basd = ""
				key_match = record[1]
				# ('爬虫内容', [('2', '测试', '测试,test', '测试'), ('1', '户户通', '户户通,恶意,安装', '户户通')])
				for km in key_match:
					sql_basd += "into BASE_ANALYSIS_SENTIMENT_DETAIL(PID,NAME,MAIN_WORD,key_WORD,TITLE,INTRODUCTION,URL,OCCUR_TIME,ORIGIN_VALUE,ORIGIN_NAME) "
					sql_basd += "values("+str(km[0])+",'"+km[1]+"','"+km[2]+"','"+km[3]+"'"
					sql_basd += sql_content
				sql += sql_basd
		except:
			export_log({"type":"拼接sql","data":record[0]})
	sql += "select 1 from dual"
	print(sql)
	if b:
		basd_info_add(sql)
	
# 检查是否有重复
# def check_sentence(http_url):
# 	sql = "select TITLE from BASE_ANALYSIS_SENTIMENT_DETAIL where URL='%s'"%http_url
# 	op = OrclPool()
# 	res_check = op.fetch_all(sql)
# 	if len(res_check)==0:
# 		return False
# 	return True

def ayls_sentence(sentence):
	# keywords = update_keywords()
	keywords = update_keywords_fromtxt()
	res = json.loads(sentence[1])
	# http_url = res['URL']
	# 如果有重复
	# if check_sentence(http_url):
	# 	return (sentence,0)
	# 获取分词列表
	conf_word = res['CONF_WORD'].lower().split('$$')
	participle = set(conf_word) # 去重
	res_match = participle.intersection(set(keywords.keys())) # 交集操作
	if len(res_match) == 0:
		return (sentence[1],0)
	else:
		# 去除同一id的集合元素，每个id包含的关键字中只保留一个
		id_list = []
		repeat_list = []
		for rm in res_match:
			kid = keywords[rm]['id']
			if kid in id_list:
				repeat_list.append(rm)
			else:
				id_list.append(kid)
		# 集合差运算
		res_match = res_match.difference(set(repeat_list))
		key_match = []
		for kw in res_match:
			vals = keywords.get(kw)
			key_match.append((vals['id'],vals['name'],vals['main_word'],kw))
		return (sentence[1],key_match)
	# return (sentence,0)

def filter_sentence(sentence):
	if sentence[1] == 0:
		return False
	return True

# 生成错误日志
def export_log(log_info):
	print('==='*30)
	print(log_info)
	print('==='*30)
	log_time = time.strftime("%Y-%m-%d", time.localtime())
	log_time1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	if not os.path.exists('/tmp/log/log_poa/'):
		os.makedirs('/tmp/log/log_poa/')
	with open('/tmp/log/log_poa/streaming-%s.log'%log_time,'a+') as fp:
		fp.write('%s:%s'%(log_time1,json.dumps(log_info,ensure_ascii=False)))
		fp.write('\n')

try:
	# sc = SparkContext(appName="analysis")
	# sc.setLogLevel("DEBUG")
	# sconf = SparkConf()
	# sc = SparkContext(appName='KafkaDirectAnalysis',conf=sconf)
	sc = SparkContext()
	sc.setLogLevel("WARN")
	# 设置时间为10秒
	ssc = StreamingContext(sc, 20)
	# 数据源
	# brokers ="172.16.54.139:6667"
	brokers ="172.16.54.139:6667,172.16.54.140:6667,172.16.54.141:6667,172.16.54.148:6667"
	topic='postsarticles'
	# 从kafka数据源获取数据
	sentences = KafkaUtils.createDirectStream(ssc,[topic],kafkaParams={"metadata.broker.list":brokers})
	sentences.pprint()
	# 对sentences做匹配处理，无用信息标记为0
	pairs = sentences.map(lambda sentence:ayls_sentence(sentence))
	# 过滤掉无用信息
	filters = pairs.filter(lambda sentence:filter_sentence(sentence))
	filters.pprint()
	# 批量存入数据库
	filters.foreachRDD(lambda rdd: rdd.foreachPartition(sendPartition))

	ssc.start()
	ssc.awaitTermination()

except py4j.protocol.Py4JJavaError as e:
	fn = 'DATA_SOURCE_ERROR'
	print('数据源错误，请检查kafka服务器是否运行正常，然后重启，已自动重启，若启动失败，请手动重启')
	restart = False
	log_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) # 获取当前时间
	if os.path.exists('../%s.log'%fn):
		mtime = os.path.getmtime('../%s.log'%fn) #获取修改时间
		m_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
		if log_time.split(':')[0]==m_time.split(':')[0]: #如果当天一小时内重启过，则生成错误日志
			restart = False
		else:
			restart = True
	else:
		restart = True
	with open('../%s.log'%fn,'w') as fp:
		fp.write('%s\n'%(log_time))
		fp.write('数据源错误，请检查kafka服务器是否运行正常，然后重启，已自动重启，若启动失败，请手动重启\n')
		fp.write('%s\n'%str(e))
	print('已生成日志：%s.log\n'%fn)
	if restart:
		print('30s后重启')
		time.sleep(30)
		os.system("./restart.sh")

except Exception as e:
	fn = 'ELSE_ERROR'
	print('**error**'*10)
	restart = False
	log_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	if os.path.exists('../%s.log'%fn):
		mtime = os.path.getmtime('../%s.log'%fn) #获取修改时间
		m_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
		if log_time.split(':')[0]==m_time.split(':')[0]: #如果当天一小时内重启过，则生成错误日志
			restart = False
		else:
			restart = True
	else:
		restart = True
	print(e)
	with open('../%s.log'%fn,'w') as fp:
		fp.write('%s\n'%(log_time))
		fp.write('%s\n'%str(e))

	print('**error**'*10)
	print('已生成日志：%s.log\n'%fn)
	if restart:
		print('30s后重启')
		time.sleep(30)
		os.system("./restart.sh")


