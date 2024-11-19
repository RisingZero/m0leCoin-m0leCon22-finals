#!/usr/bin/env python3

# Do not make modification to checklib.py (except for debug), it can be replaced at any time
import checklib
import random
import string
import sys
import os
import json
os.environ["PWNLIB_NOTERM"] = "1"

from pwn import *
import pdb
import eth_account
from s1_client import Client
from mailbox_client import Mailbox

context.timeout = 5
context.log_level = "error"

data = checklib.get_data()
action = data['action']
backend_port = int(os.getenv('BACKEND_PORT', '8000'))
mailbox = Mailbox(os.getenv('MAILBOX_URL', 'http://10.10.0.5:10000/mailbox'))
service_name = 'm0leCoin2'

team_id = data['teamId']
if args['LOCAL']:
    team_addr = '127.0.0.1'
else:
    #team_addr = '10.60.' + team_id + '.1'
    team_addr = f'm0lecoin.team{team_id}.m0lecon.fans'

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
    if args['DEBUG']:
        pdb.set_trace()
    new_account = eth_account.Account.create(extra_entropy=os.urandom(10).hex())
    password = get_random_string(random.randint(10, 16))
    
    product_content = get_random_string(random.randint(50,100))
    random_box = get_random_string(random.randint(10,20))

    c = Client(team_addr, backend_port, new_account, password, "2")

    # Test register and login of new account
    try:
        c.register()
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, "Cannot register", str(e))

    try:
        c.login()
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, "Cannot login", str(e))

    # Publish gadget
    try:
        product = c.publish_material_product(product_content)
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, "Cannot publish gadget", str(e))

    # Send gadget to myself
    try:
        c.send_material_product_by_id(product['id'], random_box)
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, "Cannot send product to mailbox", str(e))

    try:
        recvd = mailbox.get_mails(random_box)
        assert recvd == product_content
    except Exception as e:
        checklib.quit(checklib.Status.ERROR, "Failed retrieving from mailbox", str(e))

    checklib.quit(checklib.Status.OK, 'OK')


# Put the flag using the flag as the seed for random stuff
def put_flag():
    if args['DEBUG']:
        pdb.set_trace()

    flag = data['flag']

    random.seed(int.from_bytes(flag.encode(), "big"))
    
    new_account = eth_account.Account.create()
    password = get_random_string(random.randint(10, 16))

    c = Client(team_addr, backend_port, new_account, password, "2")

    try:
        c.register()
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, "Cannot register", str(e))

    # Publish gadget
    try:
        product = c.publish_material_product(flag)
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, "Cannot publish gadget", str(e))

    product_id = product["id"]

    checklib.post_flag_id(service_name, team_addr, str(product_id))

    store_round_data({
        "hmac_key": new_account.key.hex(),
        "flag_id": product_id
    })

    # If OK
    checklib.quit(checklib.Status.OK, 'OK')


# Check if the flag still exists, use the flag as the seed for random stuff as for put flag
def get_flag():
    if args['DEBUG']:
        pdb.set_trace()

    flag = data['flag']

    random.seed(int.from_bytes(flag.encode(), "big"))

    flag_stats = read_round_data()

    flag_id = flag_stats["flag_id"]
    new_account = eth_account.Account.create()
    password = get_random_string(random.randint(10, 16))

    random_box = get_random_string(random.randint(10,20))

    c = Client(team_addr, backend_port, new_account, password, "2")

    try:
        c.register()
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, "Flag getter cannot register", str(e))

    try:
        c.send_material_product_by_id(flag_id, random_box, flag_stats["hmac_key"].encode())
        recvd = mailbox.get_mails(random_box)
        assert recvd == flag
    except Exception as e:
        checklib.quit(checklib.Status.DOWN, "Failed retrieving from mailbox", str(e))

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
