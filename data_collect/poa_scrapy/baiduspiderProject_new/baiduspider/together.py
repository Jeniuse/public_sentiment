import os
import threading
import time
import sys
def baiduspider():
    os.system("scrapy crawl baidu")
    time.sleep(100)
def hhtspider():
    os.system("scrapy crawl hht")
    time.sleep(50)
def jdwxspider():
    os.system("scrapy crawl jdwx")
    time.sleep(50)
def wszgspider():
    os.system("scrapy crawl wszg")
    time.sleep(10)
	
	
def run1():
    while(True):
        t1 = threading.Thread(target=baiduspider)
        t1.start()
        t1.join()
        print(" Sbaidu  执行完成一轮")
        time.sleep(20)#执行一轮后休眠时间
		
def run2():
    while(True):
        t2 = threading.Thread(target=hhtspider)
        t2.start()
        t2.join()
        print(" hhtsc 执行完成一轮")
        time.sleep(20)#执行一轮后休眠时间
		 
def run3():
    while(True):
        t3 = threading.Thread(target=jdwxspider)
        t3.start()
        t3.join()
        print(" jdwxbz 执行完成一轮")
        time.sleep(20)#执行一轮后休眠时间

def run4():
    while(True):
        t4 = threading.Thread(target=wszgspider)
        t4.start()
        t4.join()
        print(" wszgcs 执行完成一轮")
        time.sleep(20)#执行一轮后休眠时间

def main():
    count = 0
    fp = open('out_put', 'w')#用来输出错误信息
    stderr = sys.stderr
    sys.stderr = fp

    threads = []

    ta = threading.Thread(target=run1)
    threads.append(ta)
    tb = threading.Thread(target=run2)
    threads.append(tb)
    tc = threading.Thread(target=run3)
    threads.append(tc)
    td = threading.Thread(target=run4)
    threads.append(td) 
	
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    fp.close()
    sys.stderr = stderr

main()
