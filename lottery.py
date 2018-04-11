#!/usr/bin/python3

import json
import hashlib
import sys
from web3 import Web3, HTTPProvider, IPCProvider

web3 = Web3 (HTTPProvider ("http://localhost:9545"))

#Account Class
class Account:
    def __init__(self, choice, randonNumber, address):
        self.choice = choice
        self.randomNumber = randonNumber
        self.address = address
        
    def hash (self):
        data = int.to_bytes (self.choice, 32, "big") + int.to_bytes (self.randomNumber, 32, "big")
        hash_nr = hashlib.sha256 (data).hexdigest ()
        return hash_nr
    
    def play (self, hashValue, contract):
        contract.transact ({
            "from": self.address,
            "value": web3.toWei (1.0, "ether")
        }).play (Web3.toBytes (hexstr = hashValue))
    
    def getBalance (self):
        balance = web3.eth.getBalance (self.address)
        return balance
    
    def setWinningNumber (self, number, contract):
        contract.transact ({
                "from": self.address
            }).winning (30)

    def reveal (self, contract):
        contract.transact ({
                "from": self.address
            }).reveal (self.randomNumber)
    
    def done (self, contract):
        contract.transact ({
                "from": self.address
                }).done()
    
# Read the ABI
with open ("abi.json") as f:
    abi = json.load (f)

# Get the contract address
if len (sys.argv) == 2:
    contract_address = sys.argv[1]
else:
    block_number = web3.eth.blockNumber
    contract_address = None
    while contract_address == None and block_number >= 0:
        block = web3.eth.getBlock (block_number)
        for tx_hash in block.transactions:
            tx = web3.eth.getTransactionReceipt (tx_hash)
            contract_address = tx.get ("contractAddress") 
            if contract_address != None:
                break
        block_number = block_number - 1
contract = web3.eth.contract (abi = abi, address = contract_address)
print ("Using contract address {:s}\n".format (contract_address))

# Instantiating Accounts
owner = Account(0,0,web3.eth.accounts[0])
account1 = Account(30,199,web3.eth.accounts[1])
account2  = Account(30,200,web3.eth.accounts[2])
account3 = Account(23,201,web3.eth.accounts[3])
account4 = Account(45,202,web3.eth.accounts[4])
account5 = Account(11,203,web3.eth.accounts[5])

#Add all accounts except owner to an array
players = [account1, account2, account3, account4, account5]

#Submit hash to smart contract
for i in range (0, len(players)):
    print("Using account {:d} with address {:s} to play on contract {:}".format (i+1, players[i].address, contract_address))
    
    #hash current player's choice with random number
    currHash = players[i].hash()
    
    #submit current players hash with required eth 
    players[i].play(currHash, contract)

print()    

#Printing the balance of all accounts
for i in range (0, len(players)):
    print("Account {:d} has {:.20f} ETH".format (i+1, float(web3.fromWei (players[i].getBalance(), "ether"))))

print()    
#Owner submits winning number to 30
owner.setWinningNumber(30, contract)

#Reveal on all accounts using each account's random number
for i in range (0, len(players)):
    try:
        players[i].reveal(contract)
        print ("Using account {:d} with address {:s} to reveal on contract {:s}".format (i+1, players[i].address, contract_address))
    except ValueError:
        print("Account {:d} with address {:s} is not a winner.".format (i+1, players[i].address))

print()  

#Owner calls done.
owner.done (contract)

#Print the balance of all accounts
for i in range (0, len(players)):
    print("Account {:d} with address {:s} has {:.20f} ETH".format (i+1, players[i].address, players[i].getBalance()))










