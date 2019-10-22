import requests
from time import time
import random
import json


def test(SENDER, RECIPIENT, PRIV_KEY, ADDRS, LIST_NOS):
    def path_server(relative):
        return '{}{}'.format(ADDRS, relative)

    def transactions_create(SENDER, RECIPIENT, PRIV_KEY):
        return requests.post(path_server('/transactions/create'), json={
            'sender': SENDER,
            'recipient': RECIPIENT,
            'amount': random.uniform(0.00000001, 100),
            'timestamp': int(time()),
            'privKey': PRIV_KEY,
        })

    requests.post(path_server('/nodes/register'), json={
        'node_list': LIST_NOS
    })

    # Cria 5 blocos, incluindo o Genesis, contendo de 1-4 transações cada, com valores aleatórios, entre os endereços indicados em sender e recipient.
    for x in range(0, 4):
        for y in range(0, random.randint(1, 4)):
            r = transactions_create(SENDER, RECIPIENT, PRIV_KEY)
            # r = requests.get(path_server('/transactions/mempool')) # APENAS PARA VISUALIZACAO
        
        r = requests.get(path_server('/nodes/resolve'))
        # cria um novo block e minera as transacoes do mempool nele
        r = requests.get(path_server('/mine'))

    r = requests.get(path_server('/chain'))

    # imprime o chain com todos os blocos e transacoes
    print(json.dumps(r.json(), sort_keys=True, indent=4))