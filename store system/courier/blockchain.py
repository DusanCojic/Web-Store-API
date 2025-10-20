from solcx import install_solc, set_solc_version, compile_standard
from web3 import Web3, HTTPProvider
from pathlib import Path

class GanacheClient:

    _instance = None

    def __init__(self, provider_url="http://ganache:8545"):
        # create Web3 Client
        self.provider_url = provider_url
        self.w3 = Web3(HTTPProvider(provider_url))

        # compile the contract
        self.contract_file = Path("contract.sol")
        if not self.contract_file.exists():
            raise FileNotFoundError("Contract file not found")

        self.abi, self.bytecode = self.compile_contract()

    # singleton
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def compile_contract(self):
        # set version
        install_solc("0.8.0")
        set_solc_version("0.8.0")

        # read the contract content
        source = self.contract_file.read_text()

        # compile the contract
        compiled_sol = compile_standard({
            "language": "Solidity",
            "sources": {
                "contract.sol": {
                    "content": source
                }
            },
            "settings": {
                "outputSelection": {
                    "*": {
                        "*": ["abi", "evm.bytecode.object"]
                    }
                }
            }
        })

        # extract the ABI and Bytecode of the contract
        contract_name = "OrderContract"
        abi = compiled_sol["contracts"]["contract.sol"][contract_name]["abi"]
        bytecode = compiled_sol["contracts"]["contract.sol"][contract_name]["evm"]["bytecode"]["object"]

        return abi, bytecode

    def get_owner_account(self):
        # first 10 accounts are created when initialized the system, and owners is 11th
        accounts = self.w3.eth.accounts
        if not accounts:
            raise Exception('No accounts found')

        return accounts[-1], "0xb64be88dd6b89facf295f4fd0dda082efcbe95a2bb4478f5ee582b7efe88cf60" # private key from the test

    # function to check if given address is valid and whether account associated with it has any means
    def check_address(self, address):
        if not self.w3.is_address(address):
            return False
        balance = self.w3.eth.get_balance(address)
        return balance > 0

    # function to assign courier to the contract
    def assign_courier(self, contract_address, courier_address):
        if not self.check_address(courier_address):
            return False

        owner, private_key = self.get_owner_account() # get the owners address and private key
        contract = self.w3.eth.contract(address=contract_address, abi=self.abi) # get the contract

        try:
            # create transaction for bindCourier method in the contract
            transaction = contract.functions.bindCourier(courier_address).build_transaction({
                "from": owner,
                "gas": 200_000,
                "gasPrice": self.w3.to_wei("1", "gwei"),
                "nonce": self.w3.eth.get_transaction_count(owner),
            })

            # sign the transaction with owners private key
            signed_transaction = self.w3.eth.account.sign_transaction(transaction, private_key=private_key)
            # get the transaction hash
            transaction_hash = self.w3.eth.send_raw_transaction(signed_transaction.raw_transaction)
            # wait for the receipt
            self.w3.eth.wait_for_transaction_receipt(transaction_hash)

            return True

        except Exception:
            return False

    # function to return status of a given contract
    def get_contract_status(self, contract_address):
        contract = self.w3.eth.contract(address=contract_address, abi=self.abi)
        owner, customer, courier, price, paid, delivered, courier_bound = contract.functions.getOrderState().call()
        return owner, customer, courier, price, paid, delivered, courier_bound