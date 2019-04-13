# coding:utf-8
import json
import time
import os

file_name = 'mtime.txt'
equals_time = 'False'
log_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
mtime = os.path.getmtime('spark_output.log')
m_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(mtime))
if m_time[:17]==log_time[:17]:
	equals_time = 'True'
file_size = 0.00
if os.path.exists(file_name):
	file_size = round(os.path.getsize(file_name)/float(1024*1024),2)
if file_size > 10.10:
	with open(file_name,'w') as fp:
		fp.write('%s===%s'%(log_time,m_time))
		fp.write(equals_time)
		fp.write('\n')
else:
	with open(file_name,'a+') as fp:
		fp.write('%s===%s'%(log_time,m_time))
		fp.write(equals_time)
		fp.write('\n')
