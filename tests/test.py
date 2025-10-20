from web3 import Web3
from web3 import HTTPProvider
from web3 import Account
import secrets

def create_and_initialize_account ():
    web3 = Web3 ( HTTPProvider ( "http://127.0.0.1:8545" ) )
    # create account
    private_key = "0x" + secrets.token_hex ( 32 )
    account     = Account.from_key ( private_key )
    address     = account.address

    # send funds from account 0
    result = web3.eth.send_transaction ( {
        "from": web3.eth.accounts[0],
        "to": address,
        "value": web3.to_wei ( 2, "ether" ),
        "gasPrice": 1
    } )

    return ( private_key, address )

if __name__ == "__main__":
    key1, address1 = create_and_initialize_account ()
    key2, address2 = create_and_initialize_account ()
    key3, address3 = create_and_initialize_account ()
    key4, address4 = create_and_initialize_account ()