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



@app.route('/spv/new_transaction/',methods=['post'])
def register_node():
	"""
	as spv node, create a transaction 
	"""
	values = request.get_json()

	sender = values.get('sender')
	receiver = values.get('receiver')
	amount = values.get('amount')
	block_index = values.get('block_index')


	if (sender is not None) and (receiver is not None) and (amount is not None) and (block_index is not None) and len(blockchain.blocks) >= int(block_index+1):

		blockchain.new_transaction(sender,receiver,amount,blockchain.blocks[block_index])
		response = {
			"ok":"new transaction added"
		}
	else:
		response = {
			"wrong":"wrong vars,try later"
		}

	return jsonify(response), 201




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


