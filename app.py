import json
import os
import requests
import config as config
from flask import Flask, render_template, session, request, redirect, url_for
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from datetime import datetime
from eth_keys import keys
from eth_utils import keccak

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
		block = request.args.get('block')
	else:
		block = 0
	return render_template('block_info.html',
						   page='search',
						   network=get_choose_network(),
						   block=get_block(int(block)))


@app.route('/search/transaction', methods=['GET'])
def page_transaction_info():
	if request.args.get('transaction'):
		transaction = request.args.get('transaction')
	else:
		transaction = ''
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


@app.route('/wallet/generate_key', methods=['GET'])
def page_generate_key():
	pri_key = generate_private_key()
	pub_key = calc_public_key(pri_key)
	return render_template('generate_key.html',
						   page='wallet',
						   network=get_choose_network(),
						   pri_key=pri_key.hex(),
						   pub_key=pub_key)


@app.route('/wallet/public_key', methods=['GET'])
def page_get_public_key():
	if request.args.get('key'):
		key = request.args.get('key')
	else:
		key = ''

	pub_key = calc_public_key(key)
	return render_template('get_public_key.html',
						   page='wallet',
						   network=get_choose_network(),
						   pri_key=key,
						   pub_key=pub_key)


@app.route('/wallet/balance', methods=['GET'])
def page_get_balance():
	if request.args.get('address'):
		address = request.args.get('address')
	else:
		address = ''

	balance = get_balance(address)
	return render_template('get_balance.html',
						   page='wallet',
						   network=get_choose_network(),
						   address=address,
						   balance=balance)


@app.route('/wallet/transaction', methods=['GET'])
def page_make_transaction():
	wallet_file = get_save_wallets()
	wallet_list = []
	for i in wallet_file:
		private_key = i['key']
		public_key = calc_public_key(private_key)
		wallet_list.append({
			'private_key': private_key,
			'public_key': public_key
		})
	return render_template('make_transaction.html', page='wallet', network=get_choose_network(), wallets=wallet_list)


@app.route('/wallet/transaction', methods=['POST'])
def page_do_transaction():
	if request.form.get('send'):
		s_addr_pri = request.form.get('send')
	else:
		s_addr_pri = ''

	if request.form.get('receive'):
		r_addr_pub = request.form.get('receive')
	else:
		r_addr_pub = ''

	if request.form.get('value'):
		value = request.form.get('value')
	else:
		value = ''

	if request.form.get('gas'):
		gas = request.form.get('gas')
	else:
		gas = ''

	if request.form.get('gas_price'):
		gas_price = request.form.get('gas_price')
	else:
		gas_price = ''

	if request.form.get('data'):
		data = request.form.get('data')
	else:
		data = ''

	try:
		trans = do_transaction(s_addr_pri, r_addr_pub, value, gas, gas_price, data)

		return render_template('do_transaction_success.html',
							   page='wallet',
							   network=get_choose_network(),
							   trans=trans)
	except ValueError as error:
		return render_template('do_transaction_failed.html',
							   page='wallet',
							   network=get_choose_network(),
							   error=str(error))
	except:
		return '交易失敗'


@app.route('/wallet/nft')
def page_nft():
	if request.args.get('address'):
		address = request.args.get('address')
	else:
		address = ''
	nft = get_nft(address)

	if nft.status_code == 200:
		nft_content = json.loads(nft.content)

		nfts = []

		for i in nft_content['result']:
			token_single = get_single_nft(i['token_uri'])
			nft_single = {
				'name': i['name'],
				'token_id': i['token_id'],
				'token_address': i['token_address'],
				'token_uri': i['token_uri'],
				'metadata': i['metadata'],
				'block_number_minted': i['block_number_minted'],
				'block_number': i['block_number'],
				'amount': i['amount'],
				'contract_type': i['contract_type'],
				'synced_at': i['synced_at'],
				'is_valid': i['is_valid'],
				'token_single': token_single
			}
			nfts.append(nft_single)

		return render_template('get_nft.html',
							   page='wallet',
							   network=get_choose_network(),
							   address=address,
							   nft=nft_content,
							   nfts=nfts)
	else:
		return nft.status_code


@app.route('/wallet/save', methods=['POST'])
def page_wallet_save():
	key = request.form.get('key')
	if key:
		file = open('files/account.json', 'r')
		data_origin = file.read()
		file.close()
		data = json.loads(data_origin)
		now = datetime.now()
		current_time = now.strftime("%Y/%m/%d %H:%M:%S")
		data_new = {'key': key, 'time': current_time}
		data.append(data_new)
		file = open('files/account.json', 'w')
		file.write(json.dumps(data))
		file.close()
		return render_template('save_file_success.html', page='wallet', network=get_choose_network())
	return '錢包儲存失敗'


@app.route('/wallet/list')
def page_wallet_list():
	wallet_file = get_save_wallets()
	wallet_list = []
	for i in wallet_file:
		private_key = i['key']
		public_key = calc_public_key(private_key)
		balance = get_balance(public_key)
		wallet_list.append({
			'time': i['time'],
			'private_key': private_key,
			'public_key': public_key,
			'balance': balance
		})

	return render_template('wallet_list.html',
						   page='wallet',
						   network=get_choose_network(),
						   wallets=wallet_list)


@app.route('/note')
def page_note():
	file = open('files/note.html', 'r', encoding='UTF-8')
	data = file.read()
	file.close()
	return render_template('note.html', page='note', network=get_choose_network(), content=data)


def get_save_wallets():
	file = open('files/account.json', 'r')
	data = file.read()
	wallets = json.loads(data)
	file.close()
	return wallets


def get_single_nft(url):
	result = requests.get(url)
	if result.status_code == 200:
		return json.loads(result.content)
	else:
		return {}


def get_nft(address):
	url = 'https://deep-index.moralis.io/api/v2/' + address + '/nft?chain=' + get_choose_network() + '&format=decimal'
	headers = {
		'accept': 'application/json',
		'X-API-Key': config.moralis_api_key
	}
	resp = requests.get(url, headers=headers)
	return resp


def do_transaction(s_addr_pri, r_addr_pub, value, gas, gas_price, data):
	w3 = connect_network(network=get_choose_network())
	nonce = w3.eth.getTransactionCount(calc_public_key(s_addr_pri))  # get nonce

	# 建立一個 transaction
	transaction = {
		'nonce': nonce,  # 目前這個 transaction 是 A 發送的第幾個
		'to': r_addr_pub,  # 接收者的 address
		'value': w3.toWei(value, 'wei'),  # 單位是 wei
		'gas': int(gas),  # 最多願意付多少 gas
		'gasPrice': w3.toWei(gas_price, 'gwei'),  # 每個 gas 願意付多少手續費
		'data': data.encode('utf-8').hex(),  # 夾帶的訊息
	}

	# 對 transaction 進行簽章
	signed_transaction = w3.eth.account.signTransaction(transaction, s_addr_pri)

	# 發送 raw transaction 並得到 transaction hash
	transaction_hash = w3.eth.sendRawTransaction(signed_transaction.rawTransaction)

	return transaction_hash


def get_balance(address):
	w3 = connect_network(network=get_choose_network())
	return w3.eth.getBalance(address)


def generate_private_key():
	address = Account.create('KEYSMASH FJAFJKLDSKF7JKFDJ 1530')
	return address.privateKey


def calc_public_key(key):
	address = Account.privateKeyToAccount(key)
	return address.address


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
		w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/' + config.infura_project_id))
	elif network == 'ropsten':
		w3 = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/' + config.infura_project_id))
	elif network == 'kovan':
		w3 = Web3(Web3.HTTPProvider('https://kovan.infura.io/v3/' + config.infura_project_id))
	elif network == 'goerli':
		w3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/' + config.infura_project_id))
	else:
		w3 = Web3(Web3.HTTPProvider('https://rinkeby.infura.io/v3/' + config.infura_project_id))
	w3.middleware_onion.inject(geth_poa_middleware, layer=0)
	return w3


if __name__ == '__main__':
	app.run()
