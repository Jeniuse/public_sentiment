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
with open('update_basd_sql.txt','r',encoding= 'utf8') as fp:
	sql = fp.read()

try:
	update_sql = json.loads(sql)
	for us in update_sql:
		op = OrclPool()
		op.execute_sql(us)
except Exception as e:
	export_log({"type":"update_sql","data":sql,"exception":str(e)})
