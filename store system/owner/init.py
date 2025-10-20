from web3 import Web3
import time

# try to connect to Ganache docker container
while True:
    try:
        w3 = Web3(Web3.HTTPProvider("http://ganache:8545"))
        if w3.is_connected():
            print("Connected to Ganache")
            break
        else:
            print("Not connected, retrying in 3s...")
    except Exception as e:
        print(f"⚠️ Error: {e}")
    time.sleep(3)

# get accounts for the transfer
accounts = w3.eth.accounts
sender = accounts[0]
receiver = accounts[-1]

# transfer some ETH from one of the system generated accounts to the owners account
transaction = {
    'from': sender,
    'to': receiver,
    'value': w3.to_wei(10, 'ether'),
    'gas': 21000,
    'gasPrice': w3.to_wei('1', 'gwei'),
    'nonce': w3.eth.get_transaction_count(sender)
}

# send transaction
transaction_hash = w3.eth.send_transaction(transaction)
# wait for the receipt
w3.eth.wait_for_transaction_receipt(transaction_hash)