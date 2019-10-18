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


# Exemplo de uso

Para utilizar o script com melhor eficiência, recomendo fazer um cache dos itens localmente. Edite o *cache.py* e rode o comando:

* python3 cache.py

Para gerar os arquivos *hostlist.json* e o *itemlist.json*. Com esses arquivos a consulta para os itens ficará mais rápida.

Agora edite *itemsearch.py* e rode para gerar um output parecido com esse:

<pre>
---------------------------------------
Host: Zabbix server [10084]
Item: Number of processed character values per second [10074]
Trend:
[{'itemid': '10073', 'clock': '1566738000', 'num': '9', 'value_min': '0.4166', 'value_avg': '0.5203', 'value_max': '0.5332'}, {'itemid': '10073', 'clock': '1566741600', 'num': '60', 'value_min': '0.5332', 'value_avg': '0.6261', 'value_max': '0.7664'}]
---------------------------------------
History:
[{'itemid': '10074', 'clock': '1571408034', 'value': '0.2002', 'ns': '22904035'}, {'itemid': '10074', 'clock': '1571407974', 'value': '0.1520', 'ns': '95411802'}]
---------------------------------------
</pre>

