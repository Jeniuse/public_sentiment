# coding:utf-8
import json
import time
import os
from oraclepool import OrclPool

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

sql = ""
with open('update_basd_sql.txt','r') as fp:
	sql = fp.read()

try:
	# sql = "delete from BASE_ANALYSIS_SENTIMENT_DETAIL where ID in ('111','122')"
	ID_list_str = sql.split('(')[1].split(')')[0]
	ID_list = ID_list_str.split(',')
	count = 0
	ID_list_part = []
	bsql = ''
	length = len(ID_list)
	for bid in ID_list:
		count = count + 1
		ID_list_part.append(str(bid))
		if count % 100 == 0:
			bsql = 'delete from BASE_ANALYSIS_SENTIMENT_DETAIL where ID in (%s)'%(','.join(ID_list_part))
			ID_list_part = []
			op = OrclPool()
			op.execute_sql(bsql)
			bsql = ''
		elif count == length-1:
			bsql = 'delete from BASE_ANALYSIS_SENTIMENT_DETAIL where ID in (%s)'%(','.join(ID_list_part))
			ID_list_part = []
			op = OrclPool()
			op.execute_sql(bsql)
			bsql = ''
except Exception as e:
	export_log({"type":"update_sql","data":sql,"exception":str(e)})
