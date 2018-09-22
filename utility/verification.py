from utility.hash_util import hash_block,hash_string_256
from wallet import Wallet


class Verification:
    @classmethod
    def verify_chain(cls,blockchain):
    
        for (index,block) in enumerate(blockchain):
            if index == 0:
                continue

            if block.previous_hash != hash_block(blockchain[index-1]):
                return False
            
            if not cls.valid_proof(block.transactions[:-1],block.previous_hash,block.proof):
                print('Proof Of Work is not Verified')
                return False
        return True


    @classmethod
    def verify_transactions(cls,open_transaction,get_balance):
        return all([cls.verify_transaction(tx,get_balance,False) for tx in open_transaction])


    @staticmethod
    def verify_transaction(transaction,get_balance,check_funds = True):
        if check_funds:
            sender_balance = get_balance()
            return sender_balance >=transaction.amount and Wallet.verify_transaction(transaction)
        else:
            return Wallet.verify_transaction(transaction)

    @staticmethod
    def valid_proof(trasactions,last_hash,proof):
        guess = (str([tx.to_ordered_dict() for tx in trasactions])+str(last_hash)+str(proof)).encode()
        guess_hash = hash_string_256(guess)
        return guess_hash[0:2] == '00'

    