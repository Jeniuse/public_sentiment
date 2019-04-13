# -*- coding: utf-8 -*- 
import os
from oraclepool import OrclPool
import json

def update_keywords():
	keywords = {}
	op = OrclPool()
	sql = 'select * from BASE_ANALYSIS_SENTIMENT where DICT_ENABLED_VALUE=300010000000001'
	key_list = op.fetch_all(sql)
	for ld in key_list:
		key = {}
		key['id'] = ld[0]
		key['name'] = ld[1]
		key['main_word'] = ld[2]
		# key['key_word'] = ld[2].split(',')
		# keywords.append(key)
		kws = ld[2].split(',')
		# 关键字结构，结构根据匹配规则作相应调整
		for kw in kws:
			kw = kw.lower()
			keywords[kw] = key
	return keywords

keywords = update_keywords()
with open('keywords.txt','w',encoding= 'utf8') as fp:
	fp.write(json.dumps(keywords,ensure_ascii=False))