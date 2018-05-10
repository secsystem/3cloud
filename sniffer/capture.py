#coding:utf-8

import scapy_http.http as HTTP
from scapy.all import *
from scapy.error import Scapy_Exception
import time
import re
import os
from xmlrpclib import ServerProxy

count=0
pt = re.compile('(GET|POST).*(HTTP)')
ag = re.compile('(User-Agent:).*')
s = ServerProxy("http://localhost:8888")

def getURL(data):
	url = data.strip('GET')
	url = url.strip('POST')
	url = url.strip('HTTP')
	url = url.replace('%','%25')
	return url.strip()

def afterRPC(msg, attack_ip, request, time):
	res = int(msg[0]['res'])
	url = msg[0]['url']
	if res ==0:
		print "检测到恶意请求，将被记录"
		print "攻击者:" + attack_ip
        match = ag.match(request)
        if match:
            print "yes"
            print match.group()
            data = time+'|'+attack_ip+'|'+url+'|'+time+'||'
            os.system('echo "' + data +'" >> log.txt')
        #f = open('log.txt','a+')
        #f.write(data)
        #f.flush()
        #f.close()


def pktTCP(pkt):
    global count
    count=count+1
    #print count
    if HTTP.HTTPRequest or HTTP.HTTPResponse in pkt:
        src=pkt[IP].src
        srcport=pkt[IP].sport
        dst=pkt[IP].dst
        dstport=pkt[IP].dport
        res_payload=str(pkt[TCP].payload)
        if HTTP.HTTPRequest in pkt:
       	    log_time = str(time.strftime('%Y-%m-%d-%H:%M:%S',time.localtime(time.time())))
            print log_time
            print "HTTP Request:"
            #print res_payload
            match = pt.match(res_payload)   
            if match:
    	        data = str(match.group())
    		print data
    		url = getURL(data)
    		print url
    	    	afterRPC(s.rpc_ai_waf(url), src, res_payload, log_time)


        if HTTP.HTTPResponse in pkt:
            #print "HTTP Response:"
            #try:
            #    headers,body= str(test).split("\r\n\r\n", 1)
            #    print headers
            #except Exception,e:
            #   print e
            print "======================================================================"

    else:
        print pkt[IP].src,pkt[IP].sport,'->',pkt[TCP].flags
        print 'other'

sniff(filter='tcp and port 80',prn=pktTCP,iface='eth0')
