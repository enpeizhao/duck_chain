import hashlib
from time import time
import json
from uuid import uuid4
import urllib2
import requests


class Blockchain:

	def __init__(self):

		# blocks list
		self.blocks = []
		self.node_identifier = str(uuid4()).replace('-', '')
		self.fullNodeUrl  = "http://localhost:5000"
		# nodes address list
		self.nodes_list = [self.fullNodeUrl]


	def generate_genesis_block(self):
		"""
		generate genesis block	

		:return: json format block

		"""
		genesis_block = {
				"version":1,
				"index" : 1,
				"data" : [],
				"proof" : 100,
				"timestamp" : time(),
				"previous_hash" : "0000",
		}

		genesis_block["this_hash"] = self.hash(genesis_block)

		# reward the miner
		self.new_transaction(0,self.node_identifier,1,genesis_block)
		# add to the block list
		self.blocks.append(genesis_block)

		return genesis_block


	def hash(self,block):
		"""
		generate hash of a block

		:param block: <json> json format block
		:return: <json> sha256 hash of the block

		"""
		block_string = json.dumps(block, sort_keys=True).encode()
		return hashlib.sha256(block_string).hexdigest()


	def mine_new_block(self):
		"""
		solve the proof-of-work puzzle and mine a new block

		:return: <json> json format new block
		"""

		previous_block = self.blocks[-1]
		index = previous_block['index'] + 1

		# solve the pow
		proof = self.proof_of_work(previous_block)
		previous_hash = previous_block['this_hash']


		new_block = {
				"version":1,
				"index" : index,
				"data" : [],
				"proof" : proof,
				"timestamp" : time(),
				"previous_hash" : previous_hash,
		}

		new_block["this_hash"] = self.hash(new_block)

		
		return new_block

	def proof_of_work(self,previous_block):
		"""
		solve the proof-of-work,and find a proof

		:param previous_block: <json> json format block
		:return proof:<int> number to solve the pow 
		"""

		proof = 0
		while not self.validate_proof(proof,previous_block):
			proof += 1

		return proof


	def validate_proof(self,proof,previous_block):
		"""
		validate the proof that user input

		:param proof: <int>
		:param previous_block:<json> 
		:return: <bool> True if proof is valid
		"""

		previous_proof = previous_block['proof']
		previous_hash = previous_block['this_hash']

		proof_str = str( proof * previous_proof) + previous_hash

		result = hashlib.sha256(proof_str).hexdigest()
		return result[:4] == "0000"


	def new_transaction(self,sender,receiver,amount,block):
		"""
		add transaction to the block

		:param sender:<string>
		:param receiver:<string>
		:param amount:<int>
		:param block:<json>
		:return:<int> the index transaction inserted
		"""

		transaction = {
			"sender":sender,
			"receiver":receiver,
			"amount":amount,
			"timestamp":time()
		}
		block["data"].append(transaction)
		return block["index"]


	def loadUrl(self,url):
		"""
		load url content,and convert it to json

		:param url:<string>
		:return:<json> (if url respond) or <string> ("wrong" if url does not respond)
		"""
		try:
			data = urllib2.urlopen(url).read()
			return json.loads(data)

		except Exception,e:
			return "wrong"
		

	def postData(self,url,post_data):
		"""
		post data to url,and convert response to json

		:param url:<string>
		:param post_data:<json> data need to post
		:return:<json> (if url respond) or <string> ("wrong" if url does not respond)
		"""
		try:
			data = requests.post(url, data=post_data)

			return json.loads(data.text)

		except Exception,e:
			return "wrong"




