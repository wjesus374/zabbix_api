#!/usr/bin/python
# -*- encoding: utf-8 -*-

from pyzabbix import ZabbixAPI
import json
from datetime import datetime
import csv

import sys

reload(sys)
sys.setdefaultencoding('utf8')

with open('config.json', 'r') as jsonfile:
	data = json.load(jsonfile)
	for jsoninfo in data:
		if 'zbx_url' in jsoninfo:
			zbx_url = jsoninfo['zbx_url']
		if 'zbx_username' in jsoninfo:
			zbx_username = jsoninfo['zbx_username']
		if 'zbx_password' in jsoninfo:
			zbx_password = jsoninfo['zbx_password']

zapi = ZabbixAPI(zbx_url)

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
zapi.session.verify = False

zapi.login(zbx_username, zbx_password)
print("Connected to Zabbix API Version %s" % zapi.api_version())

data = {}

for h in zapi.host.get(output="extend"):
    name = h['name']
    hostid = h['hostid']
    #print(name)
    cont = 0
    for item in zapi.item.get(hostids=hostid, output="extend"):
        #print(item)
        for key,value in item.items():
            #print(key+' : '+str(value))
            data['hostname'] = name
            data[key] = str(value)
        if cont == 0:
            with open('csv/'+hostid+'.csv', 'w') as f:
                w = csv.DictWriter(f, data.keys())
                w.writeheader()
                w.writerow(data)
            cont += 1
        else:
            with open('csv/'+hostid+'.csv', 'a') as f:
                w = csv.DictWriter(f, data.keys())
                w.writerow(data)
    #break

