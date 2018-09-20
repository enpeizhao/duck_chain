from duckchain import Blockchain
from flask import Flask, jsonify, request
import json
import sys
import time
import schedule,threading

# instantiate the full node
app = Flask(__name__)
# instantiate the blockchain
blockchain = Blockchain()



@app.route('/list_blocks',methods=['get'])
def list_blocks():
	"""
	list all the blocks saved on the node
	"""
	return jsonify(blockchain.blocks),200



@app.route('/mining/mine', methods=['get'])
def mine():
	"""
	as mining node,find a proof which solves pow puzzle,send proof to full node to validate
	"""

	new_block = blockchain.mine_new_block()
	proof = new_block['proof']

	check_url = blockchain.fullNodeUrl + "/full/validate_block/?proof="+ str(proof)

	# send to full node to validate
	data = blockchain.loadUrl(check_url)

	if data == "wrong":
		
		return ( "full node is dead: " + blockchain.fullNodeUrl),200
		

	if data['reason'] == "ok":

		
		# reward miner one coin
		blockchain.new_transaction(0,blockchain.node_identifier,1,new_block)

		# add new block to blockchain
		blockchain.blocks.append(new_block)

		response = new_block

	else:
		response = {
			"wrong": data['reason']
		}
	
	return jsonify(response),200




def sync_blocks():
	"""
	sync blocks with other registered node,if any blocks on these nodes is longer,update local blockchain
	"""

	url = blockchain.fullNodeUrl + "/full/list_nodes"
	address_list = blockchain.loadUrl(url)


	if address_list == "wrong":
		print "full node is dead: " + blockchain.fullNodeUrl
		return None;

	whether_update = False

	for node_url in address_list:

		full_url = node_url + "/list_blocks"

		node_blocks = blockchain.loadUrl(full_url)

		if node_blocks == "wrong":
			print "died node :" + node_url 

			continue

		if len(node_blocks) > len(blockchain.blocks):

			whether_update = True
			blockchain.blocks = node_blocks


	if whether_update:
		add_str = "chain updated to length: " + str(len(blockchain.blocks))
	else: 
		add_str = "no changes"

	response = {
		"status": "compared :" + str(len(address_list)) + " nodes, " + add_str
	}	

	print(response)





def run_app(port_num):
	"""
	start server
	"""
	app.run(host='0.0.0.0', port=port_num)


if __name__ == "__main__":

	# register node
	url = blockchain.fullNodeUrl+'/full/register_node/'
	address = "http://localhost:"+str(sys.argv[1])

	post_data = json.dumps({"address": address})

	data = blockchain.postData(url,post_data)

	if data != "wrong":
	
		if data['back'] == "ok":

			print  "add address: " + address + "\n\n"

			# run server
			threading.Thread(target=run_app,args=(sys.argv[1],)).start()

			# sync blockchain every 10 seconds
			schedule.every(10).seconds.do(sync_blocks)
			while True:
				schedule.run_pending()

		else:
			print "address exists,please change other one !"
	 	 
	else:
		print "full node is dead: " + blockchain.fullNodeUrl


