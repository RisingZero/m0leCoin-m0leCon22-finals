from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
import requests, eth_account, json, os, random

with open('abi/token.abi', 'r') as f:
    token_abi = json.load(f)
with open('abi/shop.abi', 'r') as f:
    shop_abi = json.load(f)
with open('abi/bank.abi', 'r') as f:
    bank_abi = json.load(f)
with open('user-agents.txt', 'r') as f:
    ua_list = f.readlines()


class Client():
    def __init__(self, server_ip, server_port, w3_endpoint, w3_account, password, service, token_addr, shop_addr, bank_addr):
        self.server_addr = server_ip
        self.server_port = server_port
        self.base_url = f"https://{server_ip}:{server_port}/api"
        self.account = w3_account
        self.password = password
        self.service = service
        self.jwt_token = None
        self.w3 = Web3(HTTPProvider(w3_endpoint))
        assert self.w3.isConnected() == True
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.w3.eth.default_account = self.account
        self.token_contract = self.w3.eth.contract(address=token_addr,abi=token_abi)
        self.shop_contract = self.w3.eth.contract(address=shop_addr,abi=shop_abi)
        self.bank_contract = self.w3.eth.contract(address=bank_addr,abi=bank_abi)


    def get_auth_headers(self):
        return {
            "Authorization": f"Bearer {self.jwt_token}",
            "User-Agent": random.choice(ua_list)[:-1]
        }


    def txs_details(self):
        return {
            "from": self.account.address,
            "gasPrice": self.w3.eth.gas_price,
            "nonce": self.w3.eth.get_transaction_count(self.account.address)
        }


    def signTxAndSend(self, tx):
        tx_signed = self.w3.eth.account.sign_transaction(tx, private_key=self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(tx_signed.rawTransaction)
        result = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        assert result['status'] == 1
        return True


    def register(self):
        otp_response = requests.get(self.base_url + f"/otp?address={self.account.address}", headers={"User-Agent": random.choice(ua_list)[:-1]})
        assert otp_response.status_code == 200
        otp = otp_response.json()["otp"]
        signable = eth_account.messages.encode_defunct(text=otp)
        sign = eth_account.Account.sign_message(signable, self.account.key)
        register_response = requests.post(
            self.base_url + f"/register", 
            json = {
                "address": self.account.address,
                "password": self.password,
                "otpSign": sign.signature.hex()
            },
            headers={"User-Agent": random.choice(ua_list)[:-1]}
        )
        assert register_response.status_code == 200
        register_response = register_response.json()
        assert register_response["success"] == True
        self.jwt_token = register_response["token"]
        return True


    def login(self):
        login_response = requests.post(
            self.base_url + f"/login", 
            json = {
                "address": self.account.address,
                "password": self.password
            },
            headers={"User-Agent": random.choice(ua_list)[:-1]}
        )
        assert login_response.status_code == 200
        login_response = login_response.json()
        assert login_response["success"] == True
        self.jwt_token = login_response["token"]
        return True


    def get_digital_products(self) -> list:
        response = requests.get(
            self.base_url + f"/digitalproducts",
            headers=self.get_auth_headers()
        )
        assert response.status_code == 200
        response = response.json()      ## id, title, content, seller
        return response


    def get_digital_product_by_id(self, prod_id) -> object:
        response = requests.get(
            self.base_url + f"/digitalproducts/{prod_id}",
            headers=self.get_auth_headers()
        )
        assert response.status_code == 200
        response = response.json()      ## id, title, content, seller
        return response
    

    def token_get_balance(self) -> int:
        bal = self.token_contract.functions.getBalance().call({"from": self.account.address})
        return bal


    def token_transfer_balance(self, to: str, amount: int):
        tx = self.token_contract.functions.transfer(to, amount).buildTransaction(self.txs_details())
        assert self.signTxAndSend(tx) == True

    
    ## Only admin_account can sign otp (with 0.key)
    def token_mint_coints(self, to: str, amount: int):
        otp = os.urandom(10).hex()
        signable = eth_account.messages.encode_defunct(text=otp)
        sign = eth_account.Account.sign_message(signable, self.account.key)
        v = sign.v
        r = bytes.fromhex(hex(sign.r)[2:].zfill(64))
        s = bytes.fromhex(hex(sign.s)[2:].zfill(64))
        otp_hash = bytes.fromhex(sign.messageHash.hex()[2:].zfill(64))
        tx = self.token_contract.functions.mintCoins(to, amount, v, r, s, otp_hash).buildTransaction(self.txs_details())
        assert self.signTxAndSend(tx) == True


    def bank_open_account(self, otp_hash: str, v: int, r: str, s: str):
        bal = self.token_get_balance()
        tx = self.bank_contract.functions.openAccount(v, bytes.fromhex(r[2:].zfill(64)), bytes.fromhex(s[2:].zfill(64)), bytes.fromhex(otp_hash[2:].zfill(64))).buildTransaction(self.txs_details())
        assert self.signTxAndSend(tx) == True
        assert self.bank_contract.functions.isRegistered().call({"from": self.account.address}) == True
        new_bal = self.token_get_balance()
        assert new_bal > bal


    def bank_get_balance(self) -> int:
        bal = self.bank_contract.functions.getBalance().call({"from": self.account.address})
        return bal


    def bank_deposit(self, amount: int):
        bal = self.token_get_balance()
        bank_bal = self.bank_get_balance()
        tx = self.bank_contract.functions.deposit(amount).buildTransaction(self.txs_details())
        assert self.signTxAndSend(tx) == True
        new_bal = self.token_get_balance()
        new_bank_bal = self.bank_get_balance()
        assert bank_bal + amount == new_bank_bal
        assert bal - amount == new_bal


    def bank_withdraw(self):
        bal = self.token_get_balance()
        bank_bal = self.bank_get_balance()
        tx = self.bank_contract.functions.withdraw().buildTransaction(self.txs_details())
        assert self.signTxAndSend(tx) == True
        new_bal = self.token_get_balance()
        new_bank_bal = self.bank_get_balance()
        assert new_bal == bal + bank_bal
        assert new_bank_bal == 0


    def shop_get_price(self, prod_id: int):
        prod_price = self.shop_contract.functions.getPriceById(prod_id).call({"from": self.account.address})
        return prod_price


    def shop_put_on_sale(self, prod_title: str, prod_content: str, prod_price: int) -> int:
        # Publish on backend, get prod_id
        shop_response = requests.post(
            self.base_url + "/digitalproducts",
            headers = self.get_auth_headers(),
            json = {
                "title": prod_title,
                "content": prod_content
            }
        )
        assert shop_response.status_code == 200
        shop_response = shop_response.json()
        assert "id" in shop_response.keys()
        prod_id = shop_response["id"]
        # Save price on the blockchain
        tx = self.shop_contract.functions.putOnSale(prod_id, prod_price).buildTransaction(self.txs_details())
        assert self.signTxAndSend(tx) == True
        saved_price = self.shop_contract.functions.getPriceById(prod_id).call({"from": self.account.address})
        assert saved_price == prod_price
        return prod_id


    def shop_buy(self, prod_id: int) -> object:
        # Buy on the blockchain
        tx = self.shop_contract.functions.buy(prod_id).buildTransaction(self.txs_details())
        assert self.signTxAndSend(tx) == True
        # Retrieve product content
        product = self.get_digital_product_by_id(prod_id)      # id, title, content, seller
        return product


    def sendETH(self, to, amount):
        tx = self.txs_details()
        tx["to"] = to
        tx["value"] = self.w3.toWei(amount, 'ether')
        tx["gas"] = 2000000
        tx["chainId"] = 1337
        assert self.signTxAndSend(tx) == True