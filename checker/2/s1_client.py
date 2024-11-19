import requests, eth_account, json, os, random, hmac

with open('user-agents.txt', 'r') as f:
    ua_list = f.readlines()


class Client():
    def __init__(self, server_ip, server_port, w3_account, password, service):
        self.server_addr = server_ip
        self.server_port = server_port
        self.base_url = f"https://{server_ip}:{server_port}/api"
        self.account = w3_account
        self.password = password
        self.service = service
        self.jwt_token = None

    def get_auth_headers(self):
        return {
            "Authorization": f"Bearer {self.jwt_token}",
            "User-Agent": random.choice(ua_list)[:-1]
        }


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
        assert register_response["success"] == True, register_response["message"]
        self.jwt_token = register_response["token"]
        self.set_gadget_key(self.account.key.hex())
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
        assert login_response["success"] == True, login_response["message"]
        self.jwt_token = login_response["token"]
        return True


    def set_gadget_key(self, key):
        set_gadget_response = requests.post(
            self.base_url + f"/set-gadget-key", 
            json = {
                "key": key
            },
            headers=self.get_auth_headers()
        )
        assert set_gadget_response.status_code == 200
        set_gadget_response = set_gadget_response.json()
        assert set_gadget_response["success"] == True, set_gadget_response["message"]


    def get_material_products(self) -> list:
        response = requests.get(
            self.base_url + f"/materialproducts",
            headers=self.get_auth_headers()
        )
        assert response.status_code == 200
        response = response.json()
        return response


    def send_material_product_by_id(self, prod_id, dest, alt_key=None):
        response = requests.post(
            self.base_url + f"/materialproducts/{prod_id}",
            headers=self.get_auth_headers(),
            json={
                "destination": dest,
                "hmac": hmac.digest(alt_key if alt_key else self.account.key.hex().encode(), dest.encode(), 'sha256').hex()
            }
        )
        assert response.status_code == 200
        response = response.json()
        assert response["success"] == True, response["message"]
    

    def publish_material_product(self, content) -> object:
        response = requests.post(
            self.base_url + f"/materialproducts",
            headers=self.get_auth_headers(),
            json={
                "content": content
            }
        )
        assert response.status_code == 200
        response = response.json()
        assert response['id'] is not None, response['content']
        return response
