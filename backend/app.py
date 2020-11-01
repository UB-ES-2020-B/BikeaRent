from flask import Flask
from db import db
from flask_migrate import Migrate
from models.booking import BookingModel
from models.moto import MotosModel
from models.account import AccountsModel

from flask_restful import Resource
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
db.init_app(app)
#app.app_context().push()

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()


class MotosList(Resource):
    def get(self):
        motos = MotosModel.query.filter_by(active = True)
        motosList = []
        for moto in motos:
            motosList.append(moto.json())
        return motosList

