from datetime import datetime
from random import random, choice, randint
from json import load, dumps
from ellipticcurve.ecdsa import Ecdsa
from ellipticcurve.privateKey import PrivateKey
from ellipticcurve.signature import Signature
from ellipticcurve.publicKey import PublicKey

class Transaction:
	@staticmethod
	def genRandomiseTranx(fromAcc=None, toAcc=None, amount=None):
		with open('UTXODb.json', 'r') as utxos:
			utxoData = load(utxos)
		
		if(fromAcc == None):
			userList = list(utxoData.keys())[:-1]
			fromAcc, gasFees = choice(userList), random()/(10**9)
			outputsData =  Transaction.__generateOutputsData(userList, fromAcc)
			inputsData = Transaction.__getInputUtxos(utxoData, fromAcc, outputsData[1], gasFees)
		else:
			userList, gasFees = [fromAcc, toAcc], random()/(10**9)
			outputsData = Transaction.__generateOutputsData(userList, fromAcc, amountToSend=amount)
			inputsData = Transaction.__getInputUtxos(utxoData, fromAcc, outputsData[1], gasFees)

		newTranx = Transaction.__createTranx(inputsData, outputsData[1], outputsData[0], gasFees)

		return newTranx
	
	@staticmethod
	def __createTranx(inputsData, value, outputsData, gasFees):
		inputTotal = inputsData[1]
		
		if inputTotal > value + gasFees:
			outputsData.append({
				"to": inputsData[0][0]['to'],
				"amount": inputTotal - value - gasFees
			})
		
		transaction = {
			"Data": {
				"input": inputsData[0],
				"output": outputsData,
			},
			"gasFees": gasFees,
			"timestamp": str(datetime.now()),
			"signer": inputsData[0][0]['to']
		}

		#Use PrivateKey to sign the Transaction
		privateKey = Transaction.__getPrivateKey(inputsData[0][0]['to'])
		signature = Ecdsa.sign(dumps(transaction), PrivateKey.fromString(privateKey))

		#Add Signature to Transaction
		transaction['signature'] = signature.toBase64()

		return transaction
	
	@staticmethod
	def __generateOutputsData(userList, fromAcc, amountToSend=None):
		userList.remove(fromAcc)
		outputsData, outputTotal = [], 0

		if amountToSend == None:
			for x in range(randint(1,3)):
				toAcc, amount = choice(userList), random()
				outputTotal += amount
				userList.remove(toAcc)
				
				outputsData.append({
					"to": toAcc,
					"amount": amount
				})
		else:
			outputTotal += float(amountToSend)
			outputsData.append({
					"to": userList[0],
					"amount": amountToSend
			})
			
		return outputsData, outputTotal

	@staticmethod
	def __getInputUtxos(utxoData, fromAcc, outputTotal, gasFees):
		inputUtxos, inputTotal = [], 0
		while(True):
			utxo = utxoData[fromAcc].pop(0)
			inputUtxos.append(utxo)
			inputTotal += utxo['amount']
			if inputTotal > outputTotal + gasFees:
				break
		
		with open('UTXODb.json', 'w') as utxos:
			utxos.write(dumps(utxoData, indent=4))
		
		return inputUtxos, inputTotal
	
	@staticmethod
	def __getPrivateKey(publicKey):
		with open('UserKeys.json', 'r') as userKeys:
			userData = load(userKeys)
		
		return userData[publicKey]
	
	@staticmethod
	def verifyTransaction(transactionData):
		signature = Signature.fromBase64(transactionData['signature'])

		transactionMessage = dict(transactionData)
		del transactionMessage['signature']
		
		return Ecdsa.verify(dumps(transactionMessage), signature, PublicKey.fromString(transactionData['signer']))
