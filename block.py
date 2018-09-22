from time import time

from utility.printable import Printable

class Block(Printable):

    def __init__(self,index,previous_hash,transactions,proof,time=time()):
        self.previous_hash = previous_hash
        self.index=index
        self.transactions=transactions
        self.proof = proof
        self.timestamp = time

    