import os
from flask import Blueprint, request, jsonify, current_app as app
from werkzeug.security import generate_password_hash,check_password_hash
from middleware import token_required
import jwt, requests, hashlib, hmac
from models import db, Users, DigitalProducts, MaterialProducts, Otps
from web3 import Web3
from eth_account.messages import encode_defunct
from web3service import shopContract, web3

api = Blueprint('api', import_name=__name__)


@api.route('/otp', methods=['GET'])
def get_otp():
    try:
        args = request.args
        if not 'address' in args.keys() or args['address'] == '':
            return jsonify({"otp": ""}), 500

        address = args['address']
        otp = os.urandom(10).hex()

        otp_db:Otps = Otps.query.filter_by(address=address).first()
        if otp_db is None:
            otp_db = Otps(address,otp)
            db.session.add(otp_db)
        else:
            otp_db.otp = otp
        db.session.commit()

        return jsonify({"otp": otp}), 200
    except Exception as e:
        return jsonify({"otp": str(e)}), 500


@api.route('/login', methods=['POST'])
def login():
    try:
        auth = request.json  
        if not auth or not auth.get('address') or not auth.get('password'): 
            return jsonify({
                "success": False,
                "message": "Couldn't authorize"
            })
        # User password verification
        user = Users.query.filter_by(address=auth['address']).first()  
        if check_password_hash(user.password, auth['password']):
            token = jwt.encode({'address' : user.address}, app.config['SECRET_KEY'], "HS256")
            return jsonify({
                "success": True,
                "message": 'Login successful',
                "token": token
            })
        return jsonify({
                "success": False,
                "message": 'Login failed, bad credentials'
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": 'Login failed'
        })


@api.route('/register', methods=['POST'])
def register():
    try:
        data = request.json 
        
        # OTP sign verification for address property
        address = data['address']
        otp_db:Otps = Otps.query.filter_by(address=address).first()
        if otp_db is None or otp_db.otp is None:
            return jsonify({
                "success": False,
                "message": "Ask for otp message to sign before"
            })
        if not Web3.isChecksumAddress(address):
            return jsonify({
                "success": False,
                "message": "Address given is not valid or checksummed"
            })
        sign = data['otpSign']
        if address != web3.eth.account.recover_message(signable_message=encode_defunct(text=otp_db.otp), signature=sign):
            return jsonify({
                "success": False,
                "message": "Sign not matching with the given address"
            })
        otp_db.otp = None

        hashed_password = generate_password_hash(data['password'], method='sha256')
        new_user = Users(address=data['address'], password=hashed_password, gadget_privatekey=None)
        db.session.add(new_user) 
        db.session.commit()
        token = jwt.encode({'address' : new_user.address}, app.config['SECRET_KEY'], "HS256") 
        return jsonify({
            "success": True,
            "message": 'Register successful',
            "token": token
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": 'Register failed: ' + str(e)
        })


@api.route('/product-sellers', methods=['GET'])
def getProductSellers():
    try:
        products = DigitalProducts.query.all()
        gadgets = MaterialProducts.query.all()

        sellers_ids = set()
        sellers_list = []
        for p in products:
            sellers_ids.add(p.seller_address)
        for g in gadgets:
            sellers_ids.add(g.seller_address)

        for seller_id in sellers_ids:
            u = Users.query.get(seller_id)
            sellers_list.append(u.serialize)

        return jsonify(sellers_list)
    except Exception as e:
        return jsonify([])


@api.route('/set-gadget-key', methods=['POST'])
@token_required
def setGadgetPrivateKey(user: Users):
    payload = request.json

    try:
        # Check if the key is a valid web3 private key
        if not web3.eth.account.from_key(payload['key']).address:
            raise Exception("Key provided is not a valid web3 private key")

        user.gadget_privatekey = payload["key"].encode().hex()
        db.session.commit()
        return jsonify({
            "success": True,
            "message": 'Key updated'
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": 'Key update failed: ' + str(e)
        })

## Digital products
@api.route('/digitalproducts', methods=['GET'])
@token_required
def getDigitalProducts(user: Users):
    products = DigitalProducts.query.order_by(DigitalProducts.id.desc()).limit(30).all()
    return jsonify([p.serializeNoContent for p in products])


@api.route('/digitalproducts/<id>', methods=['GET'])
@token_required
def getDigitalProductByIdWithContent(user: Users, id):
    product =  DigitalProducts.query.get(id)

    purchase_logs = shopContract.events.ProductSale.createFilter(fromBlock=0, toBlock='latest', argument_filters={'_id':int(id), '_to':user.address}).get_all_entries()

    if product.seller_address == user.address or len(purchase_logs) > 0:
        return jsonify(product.serialize)
    else:
        return jsonify(DigitalProducts('', '', f'ERROR: Product not bought by {user.address} or not requested by the seller.').serialize)


@api.route('/digitalproducts', methods=['POST'])
@token_required
def sellDigitalProduct(user: Users):
    payload = request.json
    try:
        product = DigitalProducts(
            seller=user.address,
            title=payload['title'],
            content=payload['content']
        )
        db.session.add(product)
        db.session.commit()
        return jsonify(product.serializeNoContent)
    except Exception as e:
        return jsonify(DigitalProducts('', '', f'ERROR: Product insert failed.').serialize)


@api.route('/digitalproducts/<id>', methods=['DELETE'])
@token_required
def deleteDigitalProduct(user: Users, id):
    try:
        product = DigitalProducts.query.get(id)

        if product.seller_address == user.address:
            db.session.delete(product)
            db.session.commit()
            return jsonify({
                "success": True,
                "message": "Product deleted."
            })
        else:
            return jsonify({
                "success": False,
                "message": "You are not the owner, delete failed."
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "There was an error."
        })


## Gadgets
@api.route('/materialproducts', methods=['GET'])
@token_required
def getMaterialProducts(user: Users):
    products = MaterialProducts.query.order_by(MaterialProducts.id.desc()).limit(50).all()
    return jsonify([p.serializeNoContent for p in products])


@api.route('/materialproducts', methods=['POST'])
@token_required
def publishMaterialProduct(user: Users):
    payload = request.json
    try:
        product = MaterialProducts(
            seller=user.address,
            content=payload['content'],
            seller_key=user.gadget_privatekey
        )
        db.session.add(product)
        db.session.commit()
        return jsonify(product.serializeNoContent)
    except Exception as e:
        print(e)
        return jsonify(MaterialProducts('', f'ERROR: Gadget insert failed.').serialize)


@api.route('/materialproducts/<id>', methods=['POST'])
@token_required
def sendMaterialProductByIdWithContent(user: Users, id):
    product: MaterialProducts =  MaterialProducts.query.get(id)
    payload = request.json

    try:
        hmac_sign = payload['hmac']
        key = bytes.fromhex(product.seller_key)

        if hmac.compare_digest(hmac_sign, hmac.digest(key, payload['destination'].encode(), 'sha256').hex()):
            res = requests.post(os.environ.get('MAILBOX_URL')+ f"/{payload['destination']}", data=product.content)
            assert res.status_code == 200
            return jsonify({
                "success": True,
                "message": "Gadget correctly sent."
            })
        else:
            return jsonify({
                "success": False,
                "message": "Gadget not sent. HMAC not valid."
            })
    except Exception as e:
        print(e)
        return jsonify({
            "success": False,
            "message": "There was an error sending the gadget. Error: " +str(e)
        })


@api.route('/materialproducts/<id>', methods=['DELETE'])
@token_required
def deleteMaterialProduct(user: Users, id):
    try:
        product = MaterialProducts.query.get(id)

        if product.seller_address == user.address:
            db.session.delete(product)
            db.session.commit()
            return jsonify({
                "success": True,
                "message": "Gadget deleted."
            })
        else:
            return jsonify({
                "success": False,
                "message": "You are not the owner, delete failed."
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "There was an error."
        })