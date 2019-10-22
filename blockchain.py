import hashlib
import json
from time import time
import copy
import random
import requests

from bitcoin.wallet import CBitcoinSecret
from bitcoin.signmessage import BitcoinMessage, VerifyMessage, SignMessage

DIFFICULTY = 4 # Quantidade de zeros (em hex) iniciais no hash válido.

class Blockchain(object):

    def __init__(self):
        self.chain = []
        self.memPool = []
        self.nodes = set() # Conjunto para armazenar os nós registrados.
        self.createGenesisBlock()

    def createGenesisBlock(self):
        self.createBlock(previousHash='0'*64, nonce=0)
        self.mineProofOfWork(self.prevBlock)

    def createBlock(self, nonce=0, previousHash=None):
        if (previousHash == None):
            previousBlock = self.chain[-1]
            previousBlockCopy = copy.copy(previousBlock)
            previousBlockCopy.pop("transactions", None)

        block = {
            'index': len(self.chain) + 1,
            'timestamp': int(time()),
            'transactions': self.memPool,
            'merkleRoot': self.generateMerkleRoot(self.memPool),
            'nonce': nonce,
            'previousHash': previousHash or self.generateHash(previousBlockCopy),
        }

        self.memPool = []
        self.chain.append(block)
        return block

    def mineProofOfWork(self, prevBlock):
        nonce = 0
        while self.isValidProof(prevBlock, nonce) is False:
            nonce += 1

        return nonce

    def createTransaction(self, sender, recipient, amount, timestamp, privKey):
        tx = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'timestamp': timestamp
        }
 
        tx['signature'] = Blockchain.sign(privKey, json.dumps(tx, sort_keys=True)).decode('utf-8')
        self.memPool.append(tx)

        return self.prevBlock['index'] + 1

    def isValidChain(self, chain):
        # Dados uma chain passada como parâmetro, faz toda a verificação se o blockchain é válido
        # 1. PoW válido
        # 2. Transações assinadas e válidas
        # 3. Merkle Root válido
        for block in self.chain:
            if not self.isValidProof(block, block['nonce']):
                return False

            for transaction in block['transactions']:
                if not self.verifySignature(transaction['sender'],transaction['signature'],transaction):
                    return False

            if not block['merkleRoot'] == self.generateMerkleRoot(block['transactions']):
                return False

        return True             

    def resolveConflicts(self):
        # Consulta todos os nós registrados, e verifica se algum outro nó tem um blockchain com mais PoW e válido. Em caso positivo,
        # substitui seu próprio chain.
        for node in self.nodes:
            if len(list(requests.get(node+"/chain"))) > len(self.chain):
                self.chain = requests.get(node)
        
        for block in self.chain:
            for transaction in self.memPool:
                if transaction in block['transactions']:
                    self.memPool.remove(transaction)

    @staticmethod
    def generateMerkleRoot(transactions):
        if (len(transactions) == 0): # Para o bloco genesis
            return '0'*64

        txHashes = [] 
        for tx in transactions:
            txHashes.append(Blockchain.generateHash(tx))

        return Blockchain.hashTxHashes(txHashes)

    @staticmethod
    def hashTxHashes(txHashes):
        if (len(txHashes) == 1): # Condição de parada.
            return txHashes[0]

        if (len(txHashes)%2 != 0): # Confere se a quantidade de hashes é par.
            txHashes.append(txHashes[-1]) # Se não for, duplica o último hash.

        newTxHashes = []
        for i in range(0,len(txHashes),2):        
            newTxHashes.append(Blockchain.generateHash(Blockchain.generateHash(txHashes[i]) + Blockchain.generateHash(txHashes[i+1])))
        
        return Blockchain.hashTxHashes(newTxHashes)

    @staticmethod
    def isValidProof(block, nonce):
        block['nonce'] = nonce
        guessHash = Blockchain.getBlockID(block)
        return guessHash[:DIFFICULTY] == '0' * DIFFICULTY 

    @staticmethod
    def generateHash(data):
        blkSerial = json.dumps(data, sort_keys=True).encode()
        return hashlib.sha256(blkSerial).hexdigest()

    @staticmethod
    def getBlockID(block):
        blockCopy = copy.copy(block)
        blockCopy.pop("transactions", None)
        return Blockchain.generateHash(blockCopy)

    def printChain(self):
        for block in reversed(self.chain):
            print(" __________________________________________________________________")
            print("| "+str(self.hashBlock(block))+" |")
            print(" ------------------------------------------------------------------")
            print("| Indice: \t Timestamp: \t\t Nonce: \t\t   |")
            print("| "+str(block['index'])+"\t\t "+str(int(block['timestamp']))+"\t\t "+str(block['nonce'])+"\t\t\t   |") 
            print("|                                                                  |")
            print("| Merkle Root:                                                     |")
            print("| "+str(block['merkleRoot'])+" |")
            print("|                                                                  |")
            print("| Transacoes:                                                      |")
            print("| "+str(block['transactions'])+ "                                                                |")
            print("|                                                                  |")
            print("| Hash do ultimo bloco:                                            |")
            print("| "+block['previousHash']+" |")
            print(" ------------------------------------------------------------------")

            if block['index'] != 0: print("                                   |")

    @property
    def prevBlock(self):
        return self.chain[-1]

    @staticmethod
    def sign(privKey, message):
        secret = CBitcoinSecret(privKey)
        msg = BitcoinMessage(message)
        return SignMessage(secret, msg)
        
    @staticmethod
    def verifySignature(address, signature, message):
        msg = BitcoinMessage(message)
        return VerifyMessage(address, msg, signature)