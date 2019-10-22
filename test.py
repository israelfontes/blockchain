import requests
from time import time
import random
import json

ADDRS = 'http://localhost:5001'

def path(relative):
    return '{}{}'.format(ADDRS, relative)

SENDER = '19sXoSbfcQD9K66f5hwP5vLwsaRyKLPgXF'
RECIPIENT = '1MxTkeEP2PmHSMze5tUZ1hAV3YTKu2Gh1N'
PRIV_KEY = 'L1US57sChKZeyXrev9q7tFm2dgA2ktJe2NP3xzXRv6wizom5MN1U'


def transactions_create():
    return requests.post(path('/transactions/create'), json={
        'sender': SENDER,
        'recipient': RECIPIENT,
        'amount': random.uniform(0.00000001, 100),
        'timestamp': int(time()),
        'privKey': PRIV_KEY,
    })

# Cria 5 blocos, incluindo o Genesis, contendo de 1-4 transações cada, com valores aleatórios, entre os endereços indicados em sender e recipient.
for x in range(0, 4):
    for y in range(0, random.randint(1,4)):
        r = transactions_create()
        # r = requests.get(path('/transactions/mempool')) # APENAS PARA VISUALIZACAO
    
    # cria um novo block e minera as transacoes do mempool nele
    r = requests.get(path('/mine'))

r = requests.get(path('/chain'))

# imprime o chain com todos os blocos e transacoes
print(json.dumps(r.json(), sort_keys=True, indent=4))