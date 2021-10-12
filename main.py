from hashlib import sha256
from json import dumps
from Transactions import Transaction
from Database import Database
from time import sleep

class MinerNode:
	def __init__(self, difficulty):
		self.difficulty = difficulty
		self.lastBlock = dict()
		self.address = sha256('MinerNode1'.encode()).hexdigest()

	def __initialize(self):
		Database.initializeUser()
		Database.initializeDB()

	def __mineBlock(self, transactionData):
		nonce, blockNumber, transactionStatus = 1, 0, 'Not Verified'

		#Verify Transaction
		if (Transaction.verifyTransaction(transactionData)):
			transactionStatus = 'Verified'
			print('\n--> Transaction Verified Successfully')
		else:
			print('\n--> Transaction cannot be Verified')
		
		#Generate Previous Hash
		previousHash = None
		if self.lastBlock == dict():
			blockNumber = 1
			previousHash = '0000000000000000000000000000000000000000000000000000000000000000'
		else:
			blockNumber = self.lastBlock['blockNumber'] + 1
			previousHash = self.lastBlock['blockHash']

		while(True):
			blockData = {
			'blockNumber': blockNumber,
			'nonce' : nonce,
			'coinbaseTranx': {
				"to": self.address,
				"amount": transactionData['gasFees']
			},
			'data': sha256(dumps(transactionData).encode()).hexdigest(),
			'transactionstatus': transactionStatus,
			'previousHash': previousHash
			}

			currentHash = sha256(dumps(blockData).encode()).hexdigest()

			if currentHash[:self.difficulty] == '0'*self.difficulty:
				blockData['blockHash'] = currentHash
				return blockData
			else:
				nonce += 1
	
	def start(self):
		print('Starting Node.....\nNode Started...\nInitializing Databases.....', end='\n')
		self.__initialize()
		print('Database Initailized.....\nStarting Functionalities......\n', end='\n')
		self.__start()

	def __start(self):
		#print(dumps(Transaction.genRandomiseTranx(), indent=2))
		while(True):
			#Generate a Randomized Transaction
			sleep(4) #To add some sense of Trueness
			newTranx = Transaction.genRandomiseTranx()
			print('--> Generated a Randomized Transaction')
			print(dumps(newTranx, indent=2))

			#Mine The Transaction in a Block
			newBlock = self.__mineBlock(newTranx)
			print('--> New Block Mined')

			#Update UTXO's database
			Database.updateUtxoDb(newTranx['Data']['output'], newBlock['coinbaseTranx'])
			print("--> Newly Generated UTXO's updated")

			#Add the newly mined Block to Blockchain
			Database.updateBlockchain(newBlock)
			print('--> New Block Added to chain of Blocks', end='\n\n')

			#Place Last Block Data in Memory
			self.lastBlock = newBlock
		
if __name__ == '__main__':
	node = MinerNode(difficulty=5)
	node.start()