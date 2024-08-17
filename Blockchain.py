Python 3.10.6 (tags/v3.10.6:9c7b4bd, Aug  1 2022, 21:53:49) [MSC v.1932 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
import hashlib
import time
import socket
import threading
import pickle
from flask import Flask, request, jsonify

# Block Class
class Block:
    def __init__(self, index, previous_hash, transactions, timestamp, validator):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.timestamp = timestamp
        self.validator = validator
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.previous_hash}{self.transactions}{self.timestamp}{self.validator}"
        return hashlib.sha256(block_string.encode()).hexdigest()

# Blockchain Class
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.validators = ["CIMB"]  # Replace with your company's name
        self.pending_transactions = []
        self.commodity_reserves = {"gold": 0, "silver": 0, "platinum": 0}

    def create_genesis_block(self):
        return Block(0, "0", [], time.time(), "CIMB")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, validator):
        if validator in self.validators:
            new_block = Block(
                index=len(self.chain),
                previous_hash=self.get_latest_block().hash,
                transactions=self.pending_transactions,
                timestamp=time.time(),
                validator=validator,
            )
            self.chain.append(new_block)
            self.pending_transactions = []
            return True
        return False

    def create_transaction(self, transaction):
        self.pending_transactions.append(transaction)
    
    def add_reserves(self, metal, amount):
        if metal in self.commodity_reserves:
            self.commodity_reserves[metal] += amount

    def get_reserves(self):
        return self.commodity_reserves

# Consensus Mechanism
class CustomConsensus:
    def __init__(self, blockchain):
        self.blockchain = blockchain

    def validate_transaction(self, transaction, validator):
        if validator == "CIMB":
            if transaction["type"] == "trade" and transaction["commodity"] in self.blockchain.get_reserves():
                if self.blockchain.get_reserves()[transaction["commodity"]] >= transaction["amount"]:
                    return True
            elif transaction["type"] == "reserve" and validator == "CIMB":
                return True
        return False

    def approve_block(self, validator):
        return self.blockchain.add_block(validator)

# Smart Contract Class
class SmartContract:
    def __init__(self, blockchain, consensus):
        self.blockchain = blockchain
        self.consensus = consensus

    def execute_trade(self, trader, commodity, amount):
        transaction = {
            "trader": trader,
            "commodity": commodity,
            "amount": amount,
            "type": "trade",
            "timestamp": time.time()
        }
        if self.consensus.validate_transaction(transaction, "CIMB"):
            self.blockchain.create_transaction(transaction)
            self.blockchain.commodity_reserves[commodity] -= amount
            return True
        return False

    def add_reserve(self, validator, commodity, amount):
        if validator == "CIMB":
            transaction = {
                "validator": validator,
                "commodity": commodity,
                "amount": amount,
                "type": "reserve",
                "timestamp": time.time()
            }
            if self.consensus.validate_transaction(transaction, validator):
                self.blockchain.create_transaction(transaction)
                self.blockchain.add_reserves(commodity, amount)
                return True
        return False

# Wallet Class
class Wallet:
    def __init__(self, owner):
        self.owner = owner
        self.balance = 0
        self.commodities = {"gold": 0, "silver": 0, "platinum": 0}

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            return True
        return False

    def add_commodity(self, commodity, amount):
        if commodity in self.commodities:
            self.commodities[commodity] += amount

    def get_balance(self):
        return self.balance

    def get_commodities(self):
        return self.commodities

# P2P Networking
class Node:
    def __init__(self, host, port, blockchain):
        self.host = host
        self.port = port
        self.peers = []
        self.blockchain = blockchain

        server_thread = threading.Thread(target=self.start_server)
        server_thread.start()

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Node started at {self.host}:{self.port}")

        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024)
                if data:
                    message = pickle.loads(data)
                    self.process_message(message)
        except:
            client_socket.close()

    def connect_to_peer(self, peer_host, peer_port):
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect((peer_host, peer_port))
        self.peers.append((peer_host, peer_port))
        self.send_message(peer_socket, self.blockchain.chain)

    def send_message(self, peer_socket, message):
        data = pickle.dumps(message)
        peer_socket.send(data)

    def process_message(self, message):
        if isinstance(message, list):
            if len(message) > len(self.blockchain.chain):
                print("Received longer blockchain, updating local chain")
                self.blockchain.chain = message
        elif isinstance(message, Block):
            if self.blockchain.get_latest_block().hash == message.previous_hash:
                print("Adding new block from peer")
                self.blockchain.add_block(message)

# Flask API
app = Flask(__name__)

blockchain = Blockchain()
consensus = CustomConsensus(blockchain)
contract = SmartContract(blockchain, consensus)

@app.route('/trade', methods=['POST'])
def trade():
    data = request.json
    trader = data['trader']
    commodity = data['commodity']
    amount = data['amount']
    
    if contract.execute_trade(trader, commodity, amount):
        return jsonify({"message": "Trade executed"}), 200
    else:
        return jsonify({"message": "Trade failed"}), 400

@app.route('/add_reserve', methods=['POST'])
def add_reserve():
    data = request.json
    validator = data['validator']
    commodity = data['commodity']
    amount = data['amount']
    
    if contract.add_reserve(validator, commodity, amount):
        return jsonify({"message": "Reserve added"}), 200
    else:
        return jsonify({"message": "Failed to add reserve"}), 400

@app.route('/reserves', methods=['GET'])
def get_reserves():
    return jsonify(blockchain.get_reserves()), 200

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            "index": block.index,
            "previous_hash": block.previous_hash,
            "transactions": block.transactions,
            "timestamp": block.timestamp,
            "validator": block.validator,
            "hash": block.hash
        })
    return jsonify(chain_data), 200

if __name__ == '__main__':
    node = Node('localhost', 5000, blockchain)
    app.run(host='0.0.0.0', port=5001)
[DEBUG ON]
[DEBUG OFF]
