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

        return accounts[
            -1], "0xb64be88dd6b89facf295f4fd0dda082efcbe95a2bb4478f5ee582b7efe88cf60"  # private key from the test

    # function to check if given address is valid and whether account associated with it has any means
    def check_address(self, address):
        if not self.w3.is_address(address):
            return False
        balance = self.w3.eth.get_balance(address)
        return balance > 0

    # function to return status of a given contract
    def get_contract_status(self, contract_address):
        contract = self.w3.eth.contract(address=contract_address, abi=self.abi)
        owner, customer, courier, price, paid, delivered, courier_bound = contract.functions.getOrderState().call()
        return owner, customer, courier, price, paid, delivered, courier_bound