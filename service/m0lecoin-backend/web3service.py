from web3 import Web3
from  abi_interfaces  import token_interface, shop_interface
import os

token_address = os.environ.get('TOKEN_CONTRACT')
shop_address  = os.environ.get('SHOP_CONTRACT')

API_WEB3_PROVIDER = os.environ.get('API_WEB3_PROVIDER')
web3 = Web3(Web3.HTTPProvider(API_WEB3_PROVIDER))

#account = web3.eth.account.from_key(os.environ.get('TEAM_PRIVATE_KEY'))

tokenContract =  web3.eth.contract(address=token_address, abi=token_interface)
shopContract = web3.eth.contract(address=shop_address, abi=shop_interface)
