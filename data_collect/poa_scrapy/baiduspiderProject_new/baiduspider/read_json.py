import json
import os
def read_json(name):
    if os.path.exists("./jsonfile/"+name+'_UrlList.json'):
    	return False
    print("首次爬取")
    return True