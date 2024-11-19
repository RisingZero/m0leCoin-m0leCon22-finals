from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import os, sys
from models import db
from web3service  import web3
from api import api

app = Flask(__name__)
cors = CORS(app)

app.config['SECRET_KEY'] = os.environ.get('API_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('API_DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)

app.register_blueprint(api, url_prefix='/api')

if (__name__ == '__main__'):
    if len(sys.argv) > 1 and sys.argv[1] == 'migrate':
        with app.app_context():
            db.create_all()
        sys.exit(0)
    app.run(host=os.environ.get('API_HOST'), port=int(os.environ.get('API_PORT')))