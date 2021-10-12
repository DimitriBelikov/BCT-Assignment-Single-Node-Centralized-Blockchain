from json import load, dumps
from ellipticcurve.privateKey import PrivateKey

class Database:
	@staticmethod
	def initializeUser():
		userKeys = {}
		for x in range(10):
			privateKey = PrivateKey()
			publicKey = privateKey.publicKey()
			userKeys[publicKey.toString()] = privateKey.toString()

		with open('UserKeys.json', 'w+') as userKey:
			userKey.write(dumps(userKeys, indent=4))

	@staticmethod
	def initializeDB():
		#Initialize Crypto Database
		with open('CryptoData.json', 'w+') as utxo:
			utxo.write(dumps([], indent=4))

		with open('UserKeys.json', 'r') as userKey:
			userData = list((load(userKey)).keys())

		#Initialize UTXO Database
		utxoData = dict()
		for x in range(10):
			utxoData[userData[x]] = [{
				'to': userData[x],
				'amount': 100
			}]
		
		with open('UTXODb.json', 'w+') as utxo:
			utxo.write(dumps(utxoData, indent=4))

	@staticmethod
	def updateUtxoDb(outputUtxos, minerUtxo):
		with open('UTXODb.json', 'r') as utxos:
			utxoData = load(utxos)
		
		#Adding utxo's to Database object
		for utxo in outputUtxos:
			utxoData[utxo['to']].append(utxo)
		
		if minerUtxo['to'] not in utxoData.keys():
			utxoData[minerUtxo['to']] = []
		utxoData[minerUtxo['to']].append(minerUtxo)
		
		#Updating the database file
		with open('UTXODb.json', 'w') as utxos:
			utxos.write(dumps(utxoData, indent=4))

	@staticmethod
	def updateBlockchain(newBlock):
		with open('CryptoData.json', 'r') as cryptoData:
			blocksData = load(cryptoData)
		
		blocksData.append(newBlock)
		blocksData = dumps(blocksData, indent=4)

		with open('CryptoData.json', 'w') as cryptoData:
			cryptoData.write(blocksData)