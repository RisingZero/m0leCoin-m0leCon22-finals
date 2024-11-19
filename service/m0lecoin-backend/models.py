from flask_sqlalchemy import SQLAlchemy
import hashlib

db = SQLAlchemy()

class Users(db.Model):
    address = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(500), nullable=False)
    gadget_privatekey = db.Column(db.String(256), nullable=True)
    digital_products = db.relationship('DigitalProducts', lazy=True)
    material_products = db.relationship('MaterialProducts', lazy=True)

    @property
    def serialize(self):
        return {
            'address': self.address,
            'gadget_key_checksum': hashlib.sha256(bytes.fromhex(self.gadget_privatekey)).hexdigest() if self.gadget_privatekey else ''
        }

class DigitalProducts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_address = db.Column(db.String(50), db.ForeignKey('users.address'), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(200), nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'seller': self.seller_address
        }

    @property
    def serializeNoContent(self):
        return {
            'id': self.id,
            'title': self.title,
            'seller': self.seller_address
        }

    def __init__(self, seller: str, title: str, content: str):
        self.seller_address = seller
        self.title = title
        self.content = content


class MaterialProducts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_address = db.Column(db.String(50), db.ForeignKey('users.address'), nullable=False)
    seller_key = db.Column(db.String(256), nullable=False)
    content = db.Column(db.String(200), nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'content': self.content,
            'owner': self.seller_address
        }

    @property
    def serializeNoContent(self):
        return {
            'id': self.id,
            'seller': self.seller_address
        }

    def __init__(self, seller: str, content: str, seller_key: str):
        self.seller_address = seller
        self.content = content
        self.seller_key = seller_key


class Otps(db.Model):
    address = db.Column(db.String(100), primary_key=True)
    otp = db.Column(db.String(25), nullable=True)

    def __init__(self, address: str, otp: str):
        self.address = address
        self.otp = otp