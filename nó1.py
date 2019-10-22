from blockchain import Blockchain
from flask import Flask
from flask import request
from flask import jsonify

BLOCKCHAIN = Blockchain()

app = Flask(__name__)


@app.route('/transactions/create', methods=['POST'])
def createTransaction():
    req = request.get_json()
    
    block = BLOCKCHAIN.createTransaction(
        sender=req['sender'],
        recipient=req['recipient'],
        amount=req['amount'],
        timestamp=req['timestamp'],
        privKey=req['privKey'],
    )

    return jsonify({
        'hash': Blockchain.generateHash(block),
        'block': BLOCKCHAIN.prevBlock,
    })


@app.route('/transactions/mempool', methods=['GET'])
def memPoolTransactions():
    return jsonify(BLOCKCHAIN.memPool)


@app.route('/mine', methods=['GET'])
def mine():
    BLOCKCHAIN.createBlock()
    BLOCKCHAIN.mineProofOfWork(BLOCKCHAIN.prevBlock)

    return jsonify({
        'hash': Blockchain.generateHash(BLOCKCHAIN.prevBlock),
        'block': BLOCKCHAIN.prevBlock,
    })
    

@app.route('/chain', methods=['GET'])
def chain():
    return jsonify({
        'chain': BLOCKCHAIN.chain
    })

@app.route('/nodes/register', methods=['POST'])
def register():
    req = request.get_json()

    nodeList = req['node_list']
    for node in nodeList:
        if node not in BLOCKCHAIN.nodes:
            BLOCKCHAIN.nodes.add(node)

    print(BLOCKCHAIN.nodes)
    
    return jsonify({
    })

@app.route('/nodes/resolve', methods=['GET'])
def resolve():
    return jsonify({
        'data': BLOCKCHAIN.resolveConflicts()
    })



if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5000', debug=True)

# Implemente sua API com os end-points indicados no GitHub.
# https://github.com/danilocurvelo/imd0293/tree/master/06-api
# Implemente um teste com ao menos 2 nós simultaneos.