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

                signature = self.wallet.sign_transaction(self.wallet.public_key,recipent,amount)
                if self.blockchain.add_transaction(recipent,self.wallet.public_key,signature,amount=amount):
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



