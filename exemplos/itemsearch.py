from pyzabbix import ZabbixAPI
import json

zapi = ZabbixAPI("http://192.168.0.16/zabbix")
zapi.login("usuario", "senha")
print("Connected to Zabbix API Version %s" % zapi.api_version())


with open('itemlist.json','r') as jsonfile:
    itemlist = json.load(jsonfile)

with open('hostlist.json','r') as jsonfile:
    hostlist = json.load(jsonfile)

for host in hostlist:
    #print(host['hostid'])
    for item in itemlist:
        #print(item)
        if host['hostid'] == item['hostid']:
            print("Host: %s [%s]" %(host['name'],host['hostid']))
            print("Item: %s [%s]" %(item['name'],item['itemid']))
            #Trend - Base de informações de estatisticas que o Zabbix armazena. 
            #O limit coleta os ultimos X registros
            print("Trend: ")
            print(zapi.trend.get(output="extend", itemid=item['itemid'], limit=2))
            print("---------------------------------------")
            # History - Base mais recente do Zabbix e é armazenada por menores periodos
            print("History: ")
            print(zapi.history.get(output="extend", itemids=item['itemid'], limit=2, history=0, sortfield="clock", sortorder="DESC"))
            print("---------------------------------------")




