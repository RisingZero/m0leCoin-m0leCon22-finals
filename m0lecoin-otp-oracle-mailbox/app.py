from time import time
from eth_account import Account, messages
from flask import Flask, request, jsonify
import redis, os

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
NUM_TEAMS = int(os.getenv('NUM_TEAMS', '12'))
TICK_SECONDS = int(os.getenv('TICK_SECONDS', '60'))
OTP_LENGTH = int(os.getenv('OTP_LENGTH', '20'))

def get_random_string():
    return os.urandom(OTP_LENGTH//2).hex()

storage = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

start_time = int(time())
for i in range(0,NUM_TEAMS):
    for j in range(0,NUM_TEAMS):
        storage.set(f'last_timestamp{j}#{i}', start_time - TICK_SECONDS)

app = Flask(__name__)

@app.route("/signature/<team_id>", methods=["GET"])
def get_registration_signature(team_id):
    # Get team from IP
    team_requesting = request.remote_addr.split(".")[2]
    #team_requesting = 1
    with open(f'keys/{team_id}.key', 'r') as f:
        account = Account.from_key(f.read())

    # Check if new otp must be generated
    last_timestamp = int(storage.get(f'last_timestamp{team_id}#{team_requesting}'))
    if (time() - last_timestamp) > TICK_SECONDS:
        otp = get_random_string()
        storage.set(f'last_timestamp{team_id}#{team_requesting}', int(time()))
        storage.set(f'otp{team_id}#{team_requesting}', otp)
    else:
        otp = storage.get(f'otp{team_id}#{team_requesting}')

    # Sign new/old otp
    signable = messages.encode_defunct(text=otp)
    sign = Account.sign_message(signable, account.key)

    return jsonify({
        "hash": sign.messageHash.hex(),
        "v": sign.v,
        "r": hex(sign.r),
        "s": hex(sign.s)
    }), 200


@app.route("/mailbox/<box>", methods=["POST"])
def save_message(box: str):
    if box.startswith('otp') or box.startswith('last_timestamp'):
        return "Invalid box name", 400

    storage.set(box, request.data)

    return "OK", 200


@app.route("/mailbox/<box>", methods=["GET"])
def get_message(box: str):
    if box.startswith('otp') or box.startswith('last_timestamp'):
        return "Invalid box name", 400
    
    msg = storage.get(box)
    if msg:
        return msg, 200
    else:
        return "Not found", 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
