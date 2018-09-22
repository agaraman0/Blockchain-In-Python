from flask import Flask,jsonify,request,send_from_directory
from flask_cors import CORS

from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__)
wallet = Wallet()
blockchain = Blockchain(wallet.public_key)
CORS(app)

@app.route('/',methods=['GET'])
def get_node_ui():
    return send_from_directory('ui','node.html')

@app.route('/network',methods=['GET'])
def get_network_ui():
    return send_from_directory('ui','network.html')

@app.route('/wallet',methods=['POST'])
def create_keys():
    wallet.create_keys()
    if wallet.save_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key)
        response = {
            'public_key':wallet.public_key,
            'private_key':wallet.private_key,
            'funds':blockchain.get_balance()
        }
        return jsonify(response),201
    else:
        response={
            'message':'Saving The keys failed'
        }
        return jsonify(response),500
@app.route('/wallet',methods=['GET'])
def load_keys():
    if wallet.load_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key)
        response = {
            'public_key':wallet.public_key,
            'private_key':wallet.private_key,
            'funds':blockchain.get_balance()
        }
        return jsonify(response),201
    else:
        response={
            'message':'Loading The keys failed'
        }
        return jsonify(response),500

@app.route('/balance',methods=['GET'])
def get_balance():
    balance = blockchain.get_balance()
    if balance != None:
        response = {
            'message':'Fatched Balance Sucessfully.',
            'funds':balance
        }
        return jsonify(response),201
    else:
        response = {
            'message':'Loading Balance Failed',
            'wallet_set_up':wallet.public_key!=None
        }
        return jsonify(response),500

@app.route('/transaction',methods=['POST'])
def add_transaction():
    if wallet.public_key == None:
        response={
            'message':'No Wallet set up'
        }
        return jsonify(response),400
    values =request.get_json()
    if not values:
        response = {
            'message':'No Data Found'
        }
        return jsonify(response),400
    required_fields = ['recipent','amount']
    if not all(fields in values for fields in required_fields):
        response={
            'message':'Required Data is Missing'
        }

        return jsonify(response),400
    recipent = values['recipent']
    amount = values['amount']
    signature = wallet.sign_transaction(wallet.public_key,recipent,amount)
    sucess=blockchain.add_transaction(recipent,wallet.public_key,signature,amount)
    if sucess:
        response={
            'message':'Sucessfully Added a transaction',
            'transaction':{
                'sender':wallet.public_key,
                'recipent':recipent,
                'amount':amount,
                'signature':signature
            },
            'funds':blockchain.get_balance()
        }
        return jsonify(response),201

    else:
        response={
            'message':'Creating a transaction failed'
        }
        return jsonify(response),500


@app.route('/mine',methods=['POST'])
def mine():
    block =blockchain.mine_block()
    if block != None:
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
        response = {
            'message':'Block Added Sucessfully',
            'Block':dict_block,
            'funds':blockchain.get_balance()
        }
        return jsonify(response),201
    else:
        response = {
            'message':'Adding Block Failed',
            'wallet_set_up':wallet.public_key!=None
        }
        return jsonify(response),500
@app.route('/transactions',methods=['GET'])
def get_open_transaction():
    transactions = blockchain.get_open_transactions()
    dict_transaction = [tx.__dict__ for tx in transactions]
    return jsonify(dict_transaction),200

@app.route('/chain',methods=['GET'])
def get_chain():
    chain_snapshot = blockchain.chain
    dict_chain = [block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dict_chain:
        dict_block['transactions']=[tx.__dict__ for tx in dict_block['transactions']]
    return jsonify(dict_chain),200


@app.route('/node',methods=['POST'])
def add_node():
    values = request.get_json()
    if not values:
        response = {
            'message':'No Data Attached' 
        }
        return jsonify(response),400
    if 'node' not in values:
        response = {
            'message':'No node Data found' 
        }
        return jsonify(response),400
    node = values['node']
    blockchain.add_peer_node(node)
    response = {
        'message':'Node Added Sucessfully',
        'all_nodes':blockchain.get_peer_nodes()
    }
    return jsonify(response),201


@app.route('/node/<node_url>',methods=['DELETE'])        
def remove_node(node_url):
    if node_url == '' or node_url == None:
        response = {
            'message':'No node found'
        }
        return jsonify(response),400
    blockchain.remove_peer_nodes(node_url)
    response={
        'message':'Node Removed',
        'all_nodes':blockchain.get_peer_nodes()
    }
    return jsonify(response),200

@app.route('/nodes',methods=['GET'])
def get_nodes():
    nodes=blockchain.get_peer_nodes()
    response={
        'all_nodes':nodes
    }
    return jsonify(response),200

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)