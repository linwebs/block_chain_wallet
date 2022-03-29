import os
import codecs

from flask import Flask, render_template, session, request, redirect, url_for
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_keys import keys
from eth_utils import keccak
import rlp

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

global w3


@app.route('/')
def page_index():
	return render_template('index.html', page='index', network=get_choose_network())


@app.route('/network', methods=['GET'])
def page_choose_network():
	return render_template('choose_network.html', page='network', network=get_choose_network())


@app.route('/network', methods=['POST'])
def set_network():
	network = request.form.get('network')
	session['network'] = network
	return redirect(url_for('page_choose_network'))

@app.route('/search')
def page_search():
	return render_template('search.html', page='search', network=get_choose_network())


@app.route('/search/highest_block')
def page_highest_block():
	return render_template('highest_block.html',
						   page='search',
						   network=get_choose_network(),
						   block_num=get_highest_block()
						   )


@app.route('/search/block', methods=['GET'])
def page_block_info():
	if request.args.get('block'):
		block_get = request.args.get('block')
	else:
		block_get = 0
	return render_template('block_info.html',
						   page='search',
						   network=get_choose_network(),
						   block=get_block(int(block_get)))


@app.route('/search/transaction', methods=['GET'])
def page_transaction_info():
	if request.args.get('transaction'):
		transaction = request.args.get('transaction')
	else:
		transaction_get = ''
	return render_template('transaction_info.html',
						   page='search',
						   network=get_choose_network(),
						   transaction=get_transaction(transaction))


@app.route('/search/to-utf-8', methods=['POST'])
def page_to_utf_8():
	data = request.form.get('data')
	return bytes.fromhex(data[2:]).decode('utf-8')

@app.route('/wallet')
def page_wallet():
	return render_template('wallet.html', page='wallet', network=get_choose_network())


@app.route('/note')
def page_note():
	return render_template('note.html', page='note', network=get_choose_network())




def get_transaction(transaction):
	w3 = connect_network(network=get_choose_network())
	return w3.eth.getTransaction(transaction)


def get_block(block_number):
	w3 = connect_network(network=get_choose_network())
	return w3.eth.getBlock(block_number)


def get_highest_block():
	w3 = connect_network(network=get_choose_network())
	return w3.eth.blockNumber


def get_choose_network():
	if session.get('network'):
		if session['network']:
			return session['network']
	return 'rinkeby'


def connect_network(network):
	if network == 'mainnet':
		w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/06d4df44ec80442d9adf6f0f34fa5483'))
	elif network == 'ropsten':
		w3 = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/06d4df44ec80442d9adf6f0f34fa5483'))
	elif network == 'kovan':
		w3 = Web3(Web3.HTTPProvider('https://kovan.infura.io/v3/06d4df44ec80442d9adf6f0f34fa5483'))
	elif network == 'goerli':
		w3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/06d4df44ec80442d9adf6f0f34fa5483'))
	else:
		w3 = Web3(Web3.HTTPProvider('https://rinkeby.infura.io/v3/06d4df44ec80442d9adf6f0f34fa5483'))
	w3.middleware_onion.inject(geth_poa_middleware, layer=0)
	return w3


if __name__ == '__main__':
	app.run()
