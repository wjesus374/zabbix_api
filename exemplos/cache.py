from pyzabbix import ZabbixAPI
import json

zapi = ZabbixAPI("http://192.168.0.16/zabbix")
zapi.login("usuario", "senha")
print("Connected to Zabbix API Version %s" % zapi.api_version())

hostlist = []
itemlist = []

print("Coletando host's")

for h in zapi.host.get(output="extend"):
    hostlist.append(h)

with open('hostlist.json','w') as jsonfile:
    json.dump(hostlist,jsonfile)


print("Coletando iten's")

for i in zapi.item.get(output="extend"):
    itemlist.append(i)

with open('itemlist.json','w') as jsonfile:
        json.dump(itemlist,jsonfile)
