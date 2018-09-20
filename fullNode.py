from duckchain import Blockchain
from flask import Flask, jsonify, request
import json
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



@app.route('/full/register_node/',methods=['post'])
def register_node():
	values = request.get_data()
	values = json.loads(values)
	address = values['address']

	if (address is not None) and (address not in blockchain.nodes_list):

		blockchain.nodes_list.append(address)
		
		response = {
			"back":"ok",
			"nodes_list":blockchain.nodes_list	
		}
	else:
		response = {
			"back":"wrong vars or node existed"
		}
	return jsonify(response), 201


@app.route('/full/list_nodes/',methods=['get'])
def list_nodes():
	"""
	list all the nodes address
	"""
	response = blockchain.nodes_list
	return jsonify(response), 200



@app.route('/full/validate_block/',methods=['get'])
def validate_new_block():
	"""
	as full node , validate the proof which mining nodes submit
	"""

	proof  = request.values.get('proof')

	if (proof is not None ) and len(blockchain.blocks) is not 0:

		previous_block =  blockchain.blocks[-1]

		if blockchain.validate_proof( int(proof) ,previous_block):
			# proof is valid
			reason = "ok"
		else:
			reason = "failed,try later!"
	else:
		reason = "full node need to load chains,try later!"

	response = {
			"reason": reason
	}
	
	return jsonify(response), 200



def sync_blocks():
	"""
	sync blocks with other registered node,if any blocks on these nodes is longer,update local blockchain
	"""

	address_list = blockchain.nodes_list

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




def run_app():
	"""
	start server
	"""
	app.run(host='0.0.0.0', port=5000)


if __name__ == "__main__":

	# mine genesis block
	blockchain.generate_genesis_block()

	# run server
	threading.Thread(target=run_app).start()

	# sync blockchain every 10 seconds
	schedule.every(10).seconds.do(sync_blocks)
	while True:
		schedule.run_pending()




