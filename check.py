from utility.verification import Verification
from blockchain import Blockchain
from uuid import uuid4
from wallet import Wallet
class Node:

    def __init__(self):
        self.wallet = Wallet() 
        self.wallet.create_keys()
        self.blockchain = Blockchain(self.wallet.public_key)

    def get_transaction_value(self):
        tx_recipent = input('Enter The Name Of Recipent: ')
        tx_amount = float(input('Enter The Amount Of Transaction: '))
        
        return tx_recipent,tx_amount


    def get_user_choice(self):
        return input("Your Choice: ")

    def print_blockchain_elements(self):
        for block in self.blockchain.chain:
            print('Loading......')
            print(block)

        else:
            print('--'*10)


    def listen_for_input(self):
        qu = True


        while qu:
            print('Please Choose')
            print('1: Add a new transaction Value')
            print('2: Mine The Blockchain')
            print('3: Print The Blockchain')
            print('4: Check Transaction Validity')
            print('5: Create Wallet')
            print('6: Load Wallet')
            print('7: Save Keys')
            print('q: Quit')
            user_in = self.get_user_choice()

            if user_in=='1':
                tx_data = self.get_transaction_value()
                recipent,amount=tx_data


                if self.blockchain.add_transaction(recipent,self.wallet.public_key,amount=amount):
                    print('Added Transaction')
                
                else:
                    print('Transaction Failed')
                
                print(self.blockchain.get_open_transactions())

            elif user_in == '2':
                if not self.blockchain.mine_block():
                    print('Mining Failed! Have U got Wallet??')
            elif user_in == '3':
                self.print_blockchain_elements()

            elif user_in == '4':
                if Verification.verify_transactions(self.blockchain.get_open_transactions(),self.blockchain.get_balance):
                    print('All Transactions Are Valid')
                else:
                    print('There Are Invalid Transactions')
            elif user_in=='5':
                self.wallet.create_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif user_in=='6':
                self.wallet.load_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif user_in=='7':
                self.wallet.save_keys()
            elif user_in =='q':
                qu = False
            else:
                print('Input is INVALID')
            if not Verification.verify_chain(self.blockchain.chain):
                self.print_blockchain_elements()
                print("Invalid Blockchain")
                break

            print('Balance of {}:{:4.2f}'.format(self.wallet.public_key,self.blockchain.get_balance()))
        else:
            print('User Left!!')
        print('Done!!!')


if __name__ == '__main__':
    node = Node()
    node.listen_for_input()



# Initalizing our blockchain list
from functools import reduce
import hashlib as hl
import json
from collections import OrderedDict
import json

from utility.hash_util import hash_block
from block import Block
from transaction import Transaction
from utility.verification import Verification
MINING_Reward = 10



class Blockchain:
    def __init__(self,hosting_node):
        genesis_block = Block(0,'',[],100,0)
        self.chain = [genesis_block]
        self.__open_transaction = []
        self.load_data()
        self.hosting_node = hosting_node

    @property
    def chain(self):
        return self.__chain[:]

    # The setter for the chain property
    @chain.setter 
    def chain(self, val):
        self.__chain = val

    def get_open_transactions(self):
        return self.__open_transaction[:]


    def save_data(self):
        try:
            with open('blockchain.txt',mode='w') as f:
                savable_chain = [block.__dict__ for block in [Block(blok.index,blok.previous_hash,[tx.__dict__ for tx in blok.transactions],blok.proof,blok.timestamp) for blok in self.__chain]]
                f.write(json.dumps(savable_chain))
                f.write('\n')
                savable_tx = [tx.__dict__ for tx in self.__open_transaction]
                f.write(json.dumps(savable_tx))
        except:
            print('Saving Failed')


    def load_data(self):
        try:
            with open('blockchain.txt',mode='r') as f:
                file_content = f.readlines()
            blockchain = json.loads(file_content[0][:-1])
            updated_blockchain = []
            for block in blockchain:
                converted_tx = [Transaction(tx['sender'],tx['recipent'],tx['amount']) for tx in block['transactions']]
                updated_block = Block(block['index'],block['previous_hash'],converted_tx,block['proof'],block['timestamp'])
                updated_blockchain.append(updated_block)
            self.chain=updated_blockchain
            open_transaction = json.loads(file_content[1])
            updated_transactions = []
            for tx in open_transaction:
                updated_transaction = Transaction(tx['sender'],tx['recipent'],tx['amount'])
                updated_transactions.append(updated_transaction)
            self.__open_transaction=updated_transactions
        except (IOError,IndexError):
            pass

    

    def proof_of_work(self):
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transaction,last_hash,proof):
            proof+=1
        return proof

    def get_balance(self):
        participant=self.hosting_node
        tx_sender = [[tx.amount for tx in block.transactions if tx.sender==participant]for block in self.__chain]
        open_tx_sender = [tx.amount for tx in self.__open_transaction if tx.sender==participant]
        tx_sender.append(open_tx_sender)
        print(tx_sender)
        amount_sent = reduce(lambda tx_sum, tx_amt:tx_sum+sum(tx_amt) if len(tx_amt) >0 else tx_sum+0,tx_sender,0)
        tx_recipent = [[tx.amount for tx in block.transactions if tx.recipent==participant]for block in self.__chain]
        amount_recieved = reduce(lambda tx_sum, tx_amt:tx_sum+sum(tx_amt) if len(tx_amt) >0 else tx_sum+0,tx_recipent,0)

        return amount_recieved-amount_sent

    def get_last_blockchain_value(self):
        '''Returns the last value of blockchain'''
        if len(self.__chain)<1:
            return None
        return self.__chain[-1]

    def add_transaction(self,recipent,sender,amount=1.0):
        '''append new value to your blockchain'''
        if self.hosting_node==None:
            return False

        transaction = Transaction(sender,recipent,amount)
        if Verification.verify_transaction(transaction,self.get_balance):
            self.__open_transaction.append(transaction)
            self.save_data()
            return True
        return False

    def mine_block(self):
        if self.hosting_node==None:
            return False
        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        reward_transaction = Transaction('MINING',self.hosting_node,MINING_Reward)
        copied_transaction=self.__open_transaction[:]
        copied_transaction.append(reward_transaction)
        block = Block(len(self.__chain),hashed_block,copied_transaction,proof)
        self.__chain.append(block)
        self.__open_transaction =[]
        self.save_data()
        return True
