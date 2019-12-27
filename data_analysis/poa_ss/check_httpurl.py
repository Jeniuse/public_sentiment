# coding:utf-8
import json
import time
import os
import sys
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

def main(argv):
	http_url = argv[1]
	try:
		sql = "select ID,PID from BASE_ANALYSIS_SENTIMENT_DETAIL where URL='%s'"%http_url
		op = OrclPool()
		res_check = op.fetch_all(sql)
		check_httpurl = []
		if len(res_check)==0:
			check_httpurl = []
		else:
			check_httpurl = [(str(rc[0]),str(rc[1])) for rc in res_check]
			print(http_url)
		with open('check_httpurl.txt','w',encoding= 'utf8') as fp:
			fp.write(json.dumps(check_httpurl,ensure_ascii=False))
	except Exception as e:
		export_log({"type":"check_sql","data":sql,"exception":str(e)})

if __name__ == "__main__":
	main(sys.argv)
