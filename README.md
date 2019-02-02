# Zabbix API

Scripts para trabalhar com a API do Zabbix

Dependência necessária pyzabbix (pip install pyzabbix) ou utilizar o que está nesse repositório.

Exemplos de utilização:

Carregar configurações com output completo (em JSON) da própria API do Zabbix. Ao carregar de um Zabbix com SSL válido, utilizar o parametro ssl:

* zapi = loadconfig('config.json','ssl','log')

Se o certificado não for válido, utilizar a opção *nossl*:

* zapi = loadconfig('newzbx.json','nossl','')

A função *gethosts* gera um output chamado *zbx_data.json* que pode facilitar a importação dos dados de um Zabbix para outro (por exemplo).


Outras funções do script serão escritas aos pouco nesse README.
