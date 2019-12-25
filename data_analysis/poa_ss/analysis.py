# coding=utf-8
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
# print(sys.getdefaultencoding())
# os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

# 获取关键字
def update_keywords_fromtxt():
	keywords = {}
	with open('../keywords.txt','r') as fp:
		keywords = json.loads(fp.read())
	return keywords

# 批量插入数据库
def basd_info_add(insert_sql, update_sql):
	# 更新
	if update_sql_list!="":
		try:
			with open('update_basd_sql.txt','w',encoding= 'utf8') as fp:
				fp.write(json.dumps(update_sql_list,ensure_ascii=False))
			os.system('python3 update_basd.py > sql_check.txt')
			print('update')
			# print(update_sql_list)
		except Exception as e:
			export_log({"type":"updatesql","data":update_sql_list,"exception":str(e)})
	# 存储
	if insert_sql != 'insert all select 1 from dual':
		try:
			with open('insert_basd_sql.txt','w',encoding= 'utf8') as fp:
				fp.write(insert_sql)
			os.system('python3 insert_basd.py > sql_check.txt')
			print('store')
			# print(insert_sql)
		except Exception as e:
			export_log({"type":"batch_insert_sql","data":insert_sql,"exception":str(e)})

# 检测时间
def check_time(res,param_time):
	split_len = 0
	try:
		split_len = len(param_time.split('-'))-1 # 时间-的个数
	except:
		return "null"
	# 时间处理
	if len(param_time)<12:
		if split_len==1:
			param_time = "%s-01 00:00:00"%param_time
		elif split_len==2:
			param_time = "%s 00:00:00"%param_time
		else:
			param_time = "%s-01-01 00:00:00"%param_time
	else:
		split_len = len(param_time.split(':'))-1 # 时间:的个数
		if split_len==0:
			param_time = "%s:00:00"%param_time
		elif split_len==1:
			param_time = "%s:00"%param_time
		else:
			param_time = param_time = "%s"%param_time
	try:
		time.strptime(param_time,"%Y-%m-%d %H:%M:%S")
	except:
		export_log({"type":"time_error","data":res})
		param_time = "null"
	return param_time

# SQL拼接
def sendPartition(iter):
	print(update_keywords_fromtxt())
	insert_sql = 'insert all '
	delete_sql = ''
	check_ID_list = []
	b = False
	for record in iter:
		try:
			b = True
			# 拼接内容部分的sql
			sql_content = ""
			res = json.loads(record[0])
			occur_time = check_time(res,res['OCCUR_TIME'])
			# 最新爬取时间
			fetch_time = check_time(res,res['FETCH_TIME'])
			# 文档最新评论时间或修改时间
			last_update_time = check_time(res,res['LAST_UPDATE_TIME'])
			if occur_time is not 'null':
				occur_time = "to_timestamp('"+occur_time+"','yyyy-mm--dd hh24:mi:ss.ff')"
			if fetch_time is not 'null':
				fetch_time = "to_timestamp('"+fetch_time+"','yyyy-mm--dd hh24:mi:ss.ff')"
			if last_update_time is not 'null':
				last_update_time = "to_timestamp('"+last_update_time+"','yyyy-mm--dd hh24:mi:ss.ff')"
			# 浏览量，如果无法爬取到，置空
			browse_size = 'null' if res['BROWSE_SIZE'] == None else str(res['BROWSE_SIZE'])
			# 评论量，如果无法爬取到，置空
			comment_size = 'null' if res['COMMENT_SIZE'] == None else str(res['COMMENT_SIZE'])
			# 点赞量，如果无法爬取到，置空
			thumbsup_size = 'null' if res['THUMBSUP_SIZE'] == None else str(res['THUMBSUP_SIZE'])
			check_ID_list = record[2] # 获取重复ID
			if len(check_ID_list)==0 : # 没有重复ID，新增
				# 简介为空的情况
				if res['INTRODUCTION'] != '':
					res['TITLE'] = res['TITLE'].replace('\'','"')
					res['INTRODUCTION'] = res['INTRODUCTION'].replace('\'','"')
					sql_content = ",'"+res['TITLE']+"','"+res['INTRODUCTION']+"','"+res['URL']+"',"+occur_time+","+res['ORIGIN_VALUE']+",'"+res['ORIGIN_NAME']+"'"
					sql_content += ","+browse_size+","+comment_size+","+thumbsup_size+","+fetch_time+","+last_update_time+") "
				else:
					if res['ORIGIN_VALUE'] == '500010000000002':
						export_log({"type":"no INTRODUCTION","data":res})
					else:
						export_log({"type":"no Reading permissions","data":res})
				if sql_content != "":
					# 拼接内容的sql，拼接关键字
					sql_basd = ""
					key_match = record[1]
					# ('爬虫内容', [('2', '测试', '测试,test', '测试'), ('1', '户户通', '户户通,恶意,安装', '户户通')])
					for km in key_match:
						sql_basd += "into BASE_ANALYSIS_SENTIMENT_DETAIL(PID,NAME,MAIN_WORD,key_WORD,TITLE,INTRODUCTION,URL,OCCUR_TIME,ORIGIN_VALUE,ORIGIN_NAME,BROWSE_SIZE,COMMENT_SIZE,THUMBSUP_SIZE,FETCH_TIME,LAST_UPDATE_TIME) "
						sql_basd += "values("+str(km[0])+",'"+km[1]+"','"+km[2]+"','"+km[3]+"'"
						sql_basd += sql_content
					insert_sql += sql_basd
			else: # 有重复数据，更新
				for basdID in check_ID_list:
					res['TITLE'] = res['TITLE'].replace('\'','"')
					res['INTRODUCTION'] = res['INTRODUCTION'].replace('\'','"')
					update_content = "" # 更新内容部分的sql
					update_content += "update BASE_ANALYSIS_SENTIMENT_DETAIL "
					update_content += "set TITLE='"+res['TITLE']+"' "
					if res['INTRODUCTION'] != '':
						update_content += "INTRODUCTION='"+res['INTRODUCTION']+"' "
					update_content += "OCCUR_TIME="+occur_time+" "
					update_content += "BROWSE_SIZE="+browse_size+" "
					update_content += "COMMENT_SIZE="+comment_size+" "
					update_content += "THUMBSUP_SIZE="+thumbsup_size+" "
					update_content += "FETCH_TIME="+fetch_time+" "
					update_content += "LAST_UPDATE_TIME="+last_update_time+" "
					update_content += "where ID="+basdID
					update_sql_list.append(update_content)
		except Exception as e:
			print(e)
			export_log({"type":"Stitching pinjie sql","data":record[0]})
	insert_sql += "select 1 from dual"
	print(insert_sql)
	if b:
		basd_info_add(insert_sql, update_sql_list)
	
# 检查是否有重复,有重复返回ID列表，无重复返回空列表
def check_sentence(http_url):
	os.system('python3 check_httpurl.py %s'%http_url)
	check_httpurl = []
	with open('./check_httpurl.txt','r') as fp:
		check_httpurl = json.loads(fp.read())
	return check_httpurl

def ayls_sentence(sentence):
	# keywords = update_keywords()
	keywords = update_keywords_fromtxt()
	res = json.loads(sentence[1])
	http_url = res['URL']
	# 获取重复ID
	check_ID_list = check_sentence(http_url)
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
		return (sentence[1],key_match,check_ID_list)
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


