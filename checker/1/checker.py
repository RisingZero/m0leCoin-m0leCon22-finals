#!/usr/bin/env python3

# Do not make modification to checklib.py (except for debug), it can be replaced at any time
import checklib
import random
import string
import sys
import os
import json
os.environ["PWNLIB_NOTERM"] = "1"

import pdb
from pwn import *
import requests
import eth_account
from s1_client import Client

context.timeout = 5
context.log_level = "error"

data = checklib.get_data()
action = data['action']
team_id = data['teamId']
backend_port = int(os.getenv('BACKEND_PORT', '8000'))
frontend_port = int(os.getenv('FRONTEND_PORT', '4200'))
w3_provider = os.getenv('API_WEB3_PROVIDER', f'http://10.10.0.4:{8545+int(team_id)}')
service_name = 'm0leCoin1'


#team_addr = '10.60.' + team_id + '.1'
team_addr = f'm0lecoin.team{team_id}.m0lecon.fans'
#team_addr = '127.0.0.1'

with open('deploy_stats.json', 'r') as f:
    contract_addresses = json.load(f)[team_id]
TOKEN_ADDRESS = contract_addresses["token"].strip()
SHOP_ADDRESS = contract_addresses["shop"].strip()
BANK_ADDRESS = contract_addresses["bank"].strip()

with open(f'keys/{team_id}.key','r') as f:
    admin_key = f.read().strip()

def get_random_string(n):
    alph = string.ascii_letters + string.digits
    return "".join(random.choice(alph) for _ in range(n))

# Create directory to store round data.
data_dir = 'data'
try:
    os.makedirs(data_dir)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise


# Read stored data for team-round
def read_round_data():
    try:
        fl = hashlib.sha256(data['flag'].encode()).hexdigest()
        with open(f'{data_dir}/{team_id}-{fl}.json', 'r') as f:
            raw = f.read()
            return json.loads(raw)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return {}


# Store data for team-round
def store_round_data(d):
    raw = json.dumps(d)
    fl = hashlib.sha256(data['flag'].encode()).hexdigest()

    with open(f'{data_dir}/{team_id}-{fl}.json', 'w') as f:
        f.write(raw)


# Check SLA
def check_sla():
    admin_account = eth_account.Account.from_key(admin_key)
    new_account = eth_account.Account.create(extra_entropy=os.urandom(10).hex())
    password = get_random_string(random.randint(10, 16))
    
    product_title = get_random_string(random.randint(12,20))
    product_content = get_random_string(random.randint(50,100))

    try:
        admin_client = Client(team_addr, backend_port, w3_provider, admin_account, '', "1", TOKEN_ADDRESS, SHOP_ADDRESS, BANK_ADDRESS)
        c = Client(team_addr, backend_port, w3_provider, new_account, password, "1", TOKEN_ADDRESS, SHOP_ADDRESS, BANK_ADDRESS)
    except Exception as e:
        checklib.quit(checklib.Status.ERROR, "Couldn't connect to blockchain", str(e))

    # Test register and login of new account
    try:
        c.register()
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, "Cannot register", str(e))

    try:
        c.login()
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, "Cannot login", str(e))

    # Test bank open account (with coin minting)
    try:
        otp = os.urandom(8).hex()
        signable = eth_account.messages.encode_defunct(text=otp)
        sign = eth_account.Account.sign_message(signable, admin_account.key)
        c.bank_open_account(sign.messageHash.hex(), sign.v, hex(sign.r), hex(sign.s))
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, "Cannot open bank account or coins not minted", str(e))

    # Test deposit
    try:
        new_bal = c.token_get_balance()
        c.bank_deposit(random.randint(1,new_bal))
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, "Cannot deposit in bank", str(e))

    try:
        c.bank_withdraw()
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, "Cannot withdraw from bank", str(e))

    # Test shop put on sale
    new_account2 = eth_account.Account.create(extra_entropy=os.urandom(10).hex())
    password2 = get_random_string(random.randint(10, 16))
    try:
        c2 = Client(team_addr, backend_port, w3_provider, new_account2, password2, "1", TOKEN_ADDRESS, SHOP_ADDRESS, BANK_ADDRESS)
    except Exception as e:
        checklib.quit(checklib.Status.ERROR, "Couldn't connect to blockchain", str(e))

    try:
        c2.register()
        bal = c.token_get_balance()
        prod_id = c2.shop_put_on_sale(product_title, product_content,random.randint(1,bal))
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, "Cannot sell items", str(e))

    # Test shop buy
    try:
        product = c.shop_buy(prod_id)
        assert product["title"] == product_title
        assert product["content"] == product_content
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, "Cannot buy items", str(e))

    # Test frontend status 200
    try:
        res = requests.get(f'https://{team_addr}:{frontend_port}')
        assert res.status_code == 200
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, "Frontend not accessible", str(e))

    checklib.quit(checklib.Status.OK, 'OK')


# Put the flag using the flag as the seed for random stuff
def put_flag():
    flag = data['flag']

    random.seed(int.from_bytes(flag.encode(), "big"))
    
    new_account = eth_account.Account.create()
    password = get_random_string(random.randint(10, 16))

    try:
        c = Client(team_addr, backend_port, w3_provider, new_account, password, "1", TOKEN_ADDRESS, SHOP_ADDRESS, BANK_ADDRESS)
    except Exception as e:
        checklib.quit(checklib.Status.ERROR, "Couldn't connect to blockchain", str(e))

    try:
        c.register()
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, "Cannot register", str(e))

    try:
        product_id = c.shop_put_on_sale(os.urandom(random.randint(10,15)).hex(), flag, random.randint(2000,3000))
        saved_product = c.get_digital_product_by_id(product_id)
        assert saved_product["content"] == flag
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, "Cannot sell flag", str(e))

    checklib.post_flag_id(service_name, team_addr, str(product_id))

    store_round_data({
        "private_key": new_account.key.hex(),
        "flag_id": product_id
    })

    # If OK
    checklib.quit(checklib.Status.OK, 'OK')


# Check if the flag still exists, use the flag as the seed for random stuff as for put flag
def get_flag():

    flag = data['flag']

    random.seed(int.from_bytes(flag.encode(), "big"))

    flag_stats = read_round_data()

    owner_account = eth_account.Account.from_key(flag_stats["private_key"])
    flag_id = flag_stats["flag_id"]
    owner_password = get_random_string(random.randint(10, 16))
    buyer_account = eth_account.Account.create()
    buyer_password = get_random_string(random.randint(10, 16))
    admin_account = eth_account.Account.from_key(admin_key)

    try:
        admin_client = Client(team_addr, backend_port, w3_provider, admin_account, '', "1", TOKEN_ADDRESS, SHOP_ADDRESS, BANK_ADDRESS)
        owner_c = Client(team_addr, backend_port, w3_provider, owner_account, owner_password, "1", TOKEN_ADDRESS, SHOP_ADDRESS, BANK_ADDRESS)
        buyer_c = Client(team_addr, backend_port, w3_provider, buyer_account, buyer_password, "1", TOKEN_ADDRESS, SHOP_ADDRESS, BANK_ADDRESS)
    except Exception as e:
        checklib.quit(checklib.Status.ERROR, "Couldn't connect to blockchain", str(e))

    try:
        owner_c.login()
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, "Flag owner cannot login", str(e))

    try:
        product = owner_c.get_digital_product_by_id(flag_id)
        assert product["content"] == flag
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, "Flag owner cannot read flag", str(e))

    try:
        buyer_c.register()
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, "Flag buyer cannot register", str(e))

    try:
        price = buyer_c.shop_get_price(flag_id)
        admin_client.token_mint_coints(buyer_account.address, price)
        product = buyer_c.shop_buy(flag_id)
        assert product["content"] == flag
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, "Cannot buy or retrieve flag", str(e))

    checklib.quit(checklib.Status.OK, 'OK')


if __name__ == "__main__":
    START_ROUND = 0
    if int(os.environ['ROUND']) < START_ROUND:
        checklib.quit(109, 'CHECKER_DISABLED')
    if action == checklib.Action.CHECK_SLA.name:
        check_sla()
    elif action == checklib.Action.PUT_FLAG.name:
        put_flag()
    elif action == checklib.Action.GET_FLAG.name:
        get_flag()
