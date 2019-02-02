#!/usr/bin/python3
# -*- encoding: utf-8 -*-

from pyzabbix import ZabbixAPI
import json
import pprint
import re

pp = pprint.PrettyPrinter(indent=4)

#Listas com parametros de substituição
status_info = {'0':'Ativo','1':'Desativado'}
interfaces_type = {'1': 'Agente', '2': 'SNMP', '3': 'IPMI', '4': 'JMX'}
hostgroups_sub = {'TesteOLD':'TesteNEW'}
templates_sub = {'TesteOLD':'TesteNEW'}

#Lista com resposta sim
resp_sim = {'s','sim', 'Sim', 'S'}

def loadconfig(configfile, checkssl,logging):
    configfile = configfile
    checkssl = checkssl
    logging = logging

    with open(configfile, 'r') as jsonfile:
        data = json.load(jsonfile)
        for jsoninfo in data:
            if 'zbx_url' in jsoninfo:
                zbx_url = jsoninfo['zbx_url']
            if 'zbx_username' in jsoninfo:
                zbx_username = jsoninfo['zbx_username']
            if 'zbx_password' in jsoninfo:
                zbx_password = jsoninfo['zbx_password']

    zapi = ZabbixAPI(zbx_url)

    if checkssl == 'nossl':
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        zapi.session.verify = False

    if logging == 'log':
        import sys
        import logging
        stream = logging.StreamHandler(sys.stdout)
        stream.setLevel(logging.DEBUG)
        log = logging.getLogger('pyzabbix')
        log.addHandler(stream)
        log.setLevel(logging.DEBUG)

    zapi.login(zbx_username, zbx_password)
    print("Connected to Zabbix API Version %s" % zapi.api_version())
    return(zapi)

def gethosts(zapi):
    zapi = zapi

    #Dict
    data = {}

    for h in zapi.host.get(output="extend"):
        name = h['name']
        hostid = h['hostid']

        data[name] = {}
        data[name].update(h)

        print('Coletando informações do host %s' %name)
        #print(data)
        #print(h)

        interfaces = zapi.hostinterface.get(hostids=hostid, output="extend")

        data[name]['INTERFACES'] = {}
        for interface in interfaces:
            data[name]['INTERFACES'][interface['interfaceid']] = {}
            data[name]['INTERFACES'][interface['interfaceid']].update(interface)

        hostgroups = zapi.hostgroup.get(hostids=hostid, output="extend")

        data[name]['HOSTGROUPS'] = {}
        for hostgroup in hostgroups:
            data[name]['HOSTGROUPS'][hostgroup['groupid']] = {}
            data[name]['HOSTGROUPS'][hostgroup['groupid']].update(hostgroup)

        try:
            data[name]['TEMPLATES'] = {}
            for template in zapi.template.get(hostids=hostid, selectParentTemplates=["templateid","name"]):
                #print(template)
                tid = template['templateid']
                #Zabbix 4 OK
                #tid = template['templateid']
                #tname = template['name']
                templatenames = zapi.template.get(output="extend", templateids=tid)

                #Zabbix 4 OK
                #data[name]['TEMPLATES'][tname] = {}

                #print(templatenames)
                for templatename in templatenames:
                    #Zabbix 4 OK
                    #data[name]['TEMPLATES'][tname].update(templatename)
                    tname = templatename['name']
                    data[name]['TEMPLATES'][tname] = {}
                    data[name]['TEMPLATES'][tname].update(templatename)
                #print(templatename)
        except:
            print("Erro ao capturar templates do host %s" %name)
            data[name]['TEMPLATES'] = {}
            data[name]['TEMPLATES']['NULL'] = {}
            data[name]['TEMPLATES']['NULL'].update({'name':'NULL', 'templateid':'0000'})

        #Nome na tela
        #print(name)
    #pp.pprint(data)
    with open('zbx_data.json','w') as outfile:
        json.dump(data, outfile)
    return(data)

def gettemplateid(zapi,templatesname,host):
	zapi = zapi
	templatesname = templatesname
	host = host

	temid = []
	for t in templatesname:
		templates = zapi.template.get(filter={"name":t['templatename']}, output="extend")

		if templates:
			temid.append({'templateid':str(templates[0]['templateid'])})
		else:
			try:
				if templates_sub[t['templatename']]:
					print('=====================================================')
					print('Template [%s] não encontrado' %t['templatename'])
					#print('Utilizando o novo template da lista de comparação')
					templatename = templates_sub[t['templatename']]
					#print('Template similar: [%s]' %templates_sub[t['templatename']])
					print('Template similar: [%s]' %templatename)
					#templateget = zapi.template.get(filter={"host":str(templates_sub[t['templatename']])}, output="extend")
					templateget = zapi.template.get(filter={"host":str(templatename)}, output="extend")
					temid.append({'templateid':str(templateget[0]['templateid'])})

				else:
					resp = input("Template similar não encontrado, adicionar outro template ao host? [s/n] ")

					if resp in resp_sim:
						tname = input("Informe o nome do template: ")
						templateget = zapi.template.get(filter={"host":str(tname)}, output="extend")
						#print(templateget)
						if templateget:
							print('Adicionando o template [%s]: ' %templateget[0]['templateid'])
							temid.append({'templateid':str(templateget[0]['templateid'])})
						else:
							print('Template não encontrado, adicione manualmente mais tarde')
			except:                
				print('Erro ao adicionar o template na lista de templates')

	#print(temid)
	return(temid)

def gethostgroupsid(zapi,hostgroupsname):
	zapi = zapi
	hostgroupsname = hostgroupsname

	hgids = []
	for hg in hostgroupsname:
	#print(hg)
		group = zapi.hostgroup.get(filter={"name":hg['hgname']}, output="extend")
		if group:
			#print(group[0]['groupid'])
			hgids.append({'groupid':str(group[0]['groupid'])})
		else:
			try:
				if hostgroups_sub[hg['hgname']]:
					print('=====================================================')
					print("Grupo encontrado: [%s]" %hg['hgname'])
					print("Utilizando o grupo [%s]" %hostgroups_sub[hg['hgname']])
					group = zapi.hostgroup.get(filter={"name":hostgroups_sub[hg['hgname']]}, output="extend")
					hgids.append({'groupid':str(group[0]['groupid'])})
			except:
				resp = input("Grupo [%s] não encontrado no Zabbix, deseja criar? [s/n]: " %hg['hgname'])
				if resp in resp_sim:
					zapi.hostgroup.create(name=hg['hgname'])
					print('Grupo criado!')
					group = zapi.hostgroup.get(filter={"name":hg['hgname']}, output="extend")
					hgids.append({'groupid':str(group[0]['groupid'])})
	return(hgids)

def changehost(hosts):
    hosts = hosts

    #print(hosts)
    for host in hosts:
        print('=====================================================')
        print ("Host: %s" %host)
        print ("Status: %s (%s)" %(hosts[host]['status'],status_info[hosts[host]['status']]))

        templatesname = []
        print ('Templates:')
        #print(hosts[host]['TEMPLATES'])
        for t in hosts[host]['TEMPLATES']:
            print ("   * %s (%s)" %(t,hosts[host]['TEMPLATES'][t]['templateid']))
            templatesname.append({'templatename' : t})

        print('Interfaces:')
        #print(hosts[host]['INTERFACES'])
        interfaces = []
        for i in hosts[host]['INTERFACES']:
            print ("ID: %s" %i)
            print ("   * IP: %s" %hosts[host]['INTERFACES'][i]['ip'])
            print ("   * DNS: %s" %hosts[host]['INTERFACES'][i]['dns'])
            print ("   * Porta: %s" %hosts[host]['INTERFACES'][i]['port'])
            print ("   * Main: %s" %hosts[host]['INTERFACES'][i]['main'])
            print ("   * Type: %s (%s)" %(hosts[host]['INTERFACES'][i]['type'],interfaces_type[hosts[host]['INTERFACES'][i]['type']]))

            ip = hosts[host]['INTERFACES'][i]['ip']
            dns = hosts[host]['INTERFACES'][i]['dns']
            porta = hosts[host]['INTERFACES'][i]['port']
            main = hosts[host]['INTERFACES'][i]['main']
            ztype = hosts[host]['INTERFACES'][i]['type']

            interfaces.append({'type': ztype, 'main': main, 'useip': 1, 'ip': ip, 'dns': dns, 'port': porta})
        #print(interfaces)

        hostgroupsname = []
        print('Hostgroups:')
            #print(hosts[host]['HOSTGROUPS'])
        for h in hosts[host]['HOSTGROUPS']:
            print ("   * Name: %s" %hosts[host]['HOSTGROUPS'][h]['name'])
            hg = hosts[host]['HOSTGROUPS'][h]['name']

            hostgroupsname.append({'hgname': hg})

        #print(hostgroupsname)
        while True:
            print('=== Editar ==========================================')
            print('(h) Host (g) Group (i) Interface')
            print('=== Adicionar ===================Pular===============')
            print('(c) Criar host                   (x) Pular host')
            print('=====================================================')
            opt = input('Opção: ')

            #zbx_url='http://zabbix.teste.com.br'

            if opt == 'x':
                break

            if opt == 'c':
                print('=====================================================')
                resp = input('Você deseja criar o host no Zabbix ? [s/n]: ')

                if resp in resp_sim:
                    print('=====================================================')
                    print('Criando o host [%s]' %host)
                    ##############################################################
                    #Escolher o Zabbix que irá receber os dados
                    ##############################################################
                    zapi = loadconfig('newzbx.json','nossl','')
                    #zapi = loadconfig('config.json','ssl','')
                    #Adicionar um grupo para teste
                    #hostgroupsname.append({'hgname': 'LyraTESTE'})
                    hg = gethostgroupsid(zapi,hostgroupsname)
                    #Nome do host utilizado para teste
                    #host = 'Teste'
                    templatesid = gettemplateid(zapi,templatesname,host)
                    #zapi.host.create(host=host, interfaces=interfaces, groups=[{'groupid':67}], inventory_mode=0)
                    #zapi.host.create(host=host, interfaces=interfaces, proxyid='10360', groups=hg, inventory_mode=0)
                    #zapi.host.create(host=host, interfaces=interfaces, groups=hg, inventory_mode=0)
                    host = re.sub('/','_',host)
                    try:
                        zapi.host.create(host=host, interfaces=interfaces, groups=hg, templates=templatesid, inventory_mode=0)
                        #zapi.host.update(hostid=10370, proxyid='10360')
                        print('Host criado!')
                        break
                    except Exception as e:
                        print('HOST NAO CRIADO. ERRO: [%s]' %e)

            if opt == 'h':
                print('=====================================================')
                host = input('Digite o novo hostname: [%s] ' %host)
                print('Host modificado para: %s' %host)

            if opt == 'i':
                print('=====================================================')
                print('Digite os novos valores, caso desejar o mesmo valor de algum item, deixe o campo em branco')
                newip = input('Digite o novo IP da interface: [%s] ' %ip)
                newporta = input('Digite o número da porta: [%s] ' %porta)
                print(interfaces_type)
                newztype = input('Digite o numero da interface: [%s - %s] ' %(ztype,interfaces_type[ztype]))
                newdns = input ('Digite o DNS: [%s] ' %dns)

                print('=====================================================')
                print('Ao confirmar as modificações será adicionado somente essa interface.')
                resp = input('Você deseja modificar a interface? [s/n]: ')
                if resp in resp_sim:
                    print('=====================================================')
                    if newip:
                        if re.search('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', newip):
                            ip = newip
                        else:
                            print('O IP informado não parece um IP válido')
                            print('Utilizando o IP %s como IP válido' %ip)
                            print('=====================================================')
                    if newporta:
                        porta = newporta
                    if newztype:
                        ztype = newztype
                    if newdns:
                        dns = newdns
                    interfaces = {'type': ztype, 'main': 1, 'useip': 1, 'ip': ip, 'dns': dns, 'port': porta}
                    print(interfaces)
                    print('Interface modificada!')


if __name__ == "__main__":
	#zapi = loadconfig('config.json','ssl','log')
	#zapi = loadconfig('newzbx.json','nossl','')
	#hosts = gethosts(zapi)
	#Confirmar e modificar o host
	#Carregar os hosts de um arquivo JSON
	with open('zbx_data.json', 'r') as jsonfile:
		hosts = json.load(jsonfile)
	#Modificar os hosts
	changehost(hosts)

