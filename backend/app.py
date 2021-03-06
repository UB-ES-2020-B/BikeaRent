from flask import Flask, render_template
from flask_migrate import Migrate
from models.booking import BookingModel
from models.moto import MotosModel
from models.account import AccountsModel, auth
from flask_restful import Resource, Api, reqparse
from db import db
from flask_cors import CORS

from datetime import datetime

from decouple import config as config_decouple
from config import config


app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})

environment = config['development']
if config_decouple('PRODUCTION', cast=bool, default=False):
    environment = config['production']

app.config.from_object(environment)

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

# app.app_context().push()


@app.route('/')
@app.route('/home')
def render_vue():
    return render_template("index.html")


class Motos(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('model', type=str, required=True, help="This field cannot be left blank")
    parser.add_argument('active', type=bool, required=True, help="This field cannot be left blank")
    parser.add_argument('charge', type=int, required=True, help="This field cannot be left blank")
    parser.add_argument('latitude', type=float, required=True, help="This field cannot be left blank")
    parser.add_argument('longitude', type=float, required=True, help="This field cannot be left blank")
    parser.add_argument('plate', type=str, required=True, help="This field cannot be left blank")

    def get(self, id):
        moto = MotosModel.find_by_id(id)
        if moto:
            return {"moto": moto.json()}, 200
        return {"Error": "Moto with identifier {} not found".format(id)}, 404

    def post(self):
        data = self.parser.parse_args()

        try:
            new_moto = MotosModel(**data)
            new_moto.save_to_db()
            return "Moto created successfully", 201
        except:
            return {"Error": "An error occurred creating moto"}, 500

    def put(self, id):
        data = self.parser.parse_args()

        bike = MotosModel.find_by_id(id)
        if bike:
            modified_bike = MotosModel(**data)
            if bike.model == modified_bike.model and bike.active == modified_bike.active and bike.charge == modified_bike.charge and bike.latitude == modified_bike.latitude and bike.longitude == modified_bike.longitude and bike.plate == modified_bike.plate:
                return {"Error": "Bike {} is up to date".format(bike.plate)}, 400
            MotosModel.modify_bike(id, modified_bike)
            return {"bike": bike.json()}, 200
        return {"Error": "Bike with identifier {} not found".format(id)}, 404


# -------- Register  ---------------------------------------------------------- #
class Accounts(Resource):
    #@auth.login_required()
    def get(self, username):
        user = AccountsModel.find_by_username(username)
        if user:
            return user.json(), 200
        else:
            return {'message': 'There is no client with username [{}] .'.format(username)}, 404

    #@auth.login_required()
    def delete(self, username):
        user = AccountsModel.find_by_username(username)
        if not user:
            return {"message": "User not found"}, 404
        user.delete_from_db()
        return {'message': "User deleted"}, 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('firstname', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('surname', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('email', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('username', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('password', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('dni', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('dataEndDrivePermission',type=str, required=True, help="This field cannot be left blank")
        #parser.add_argument('status', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('creditCard', type=str, required=True, help="This field cannot be left blank")
        #######parser.add_argument('availableMoney', type=int, required=True, help="This field cannot be left blank")
        parser.add_argument('type', type=int, required=True, help="This field cannot be left blank")
        parser.add_argument('latitude', type=float, required=True, help="This field cannot be left blank")
        parser.add_argument('longitude', type=float, required=True, help="This field cannot be left blank")
        data = parser.parse_args()

        user = AccountsModel.find_by_username(data['username'])
        if user:
            return {"message": "User already exists"}, 400
        else:
            new_user = AccountsModel(data['firstname'], data['surname'], data['email'], data['username'], data['dni'],
                                     data['dataEndDrivePermission'], data['creditCard'],
                                     data['type'],data['latitude'], data['longitude'])
            new_user.hash_password(data['password'])
            try:
                new_user.save_to_db()
                return new_user.json(), 200
            except Exception as e:
                return {"message": "Database error"}, 500
                #return {e}

    def put(self, id):
        parser = reqparse.RequestParser()

        parser.add_argument('firstname', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('surname', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('email', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('dni', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('dataEndDrivePermission', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('creditCard', type=str, required=True, help="This field cannot be left blank")

        data = parser.parse_args()

        account = AccountsModel.find_by_id(id)
        if account:

            modified_account = AccountsModel(data['firstname'], data['surname'], data['email'], account.username,
                                             data['dni'], data['dataEndDrivePermission'], data['creditCard'],
                                             account.type, account.latitude, account.longitude)
            if account.firstname == modified_account.firstname and account.surname == modified_account.surname and account.email == modified_account.email and account.dni == modified_account.dni and account.dataEndDrivePermission == modified_account.dataEndDrivePermission and account.creditCard == modified_account.creditCard:
                return {"Error": "User {} is up to date".format(account.username)}, 400
            AccountsModel.modify_account(id, modified_account)
            return {"account": account.json()}, 200
        return {"Error": "Account with identifier {} not found".format(id)}, 404


# -------- Accounts List  ---------------------------------------------------------- #
class AccountsList(Resource):
    def get(self):
        users = AccountsModel.query.all()
        all_accounts = []
        for u in users:
            all_accounts.append(u.json())

        return {'accounts': all_accounts}, 200


# -------- Login  ---------------------------------------------------------- #
class Login(Resource):
    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help="This field cannot be left blank")
        parser.add_argument('password', type=str, required=True, help="This field cannot be left blank")

        data = parser.parse_args()
        user = AccountsModel.find_by_username(data['username'])

        if user:
            if user.verify_password(data['password']):
                token = user.generate_auth_token()
                return {'token': token.decode('ascii')}, 200
            else:
                return {"message": "Password not correct"}, 400
        else:
            return {"message": "User not found"}, 404


# -------- MotosList  ---------------------------------------------------------- #
class MotosList(Resource):
    def get(self):
        motos = MotosModel.query.filter_by(active=True)
        motosList = []
        for moto in motos:
            motosList.append(moto.json())
        return motosList


# -------- BookingList  ---------------------------------------------------------- #
class BookingList(Resource):
    def get(self):
        return BookingModel.list_orders()


# -------- Booking  ---------------------------------------------------------- #
class Booking(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('userid', type=int, required=True, help="The userid is required")
    parser.add_argument('bikeid', type=int, required=True, help="The bikeid is required")

    def get(self, userid):
        rents = BookingModel.find_by_userid(userid)

        if len(rents) == 1:
            return {"rents": rents.json()}, 200
        if len(rents) > 1:
            return {"rents": [rent.json() for rent in rents]}, 200
        return {"Error": "There are no rents for user with id {}".format(userid)}, 404

    def post(self):

        data = Booking.parser.parse_args()

        userid = data['userid']
        bikeid = data['bikeid']

        user = AccountsModel.find_by_id(userid)
        bike = MotosModel.find_by_id(bikeid)

        if user is None:
            return "User not found", 404

        if bike is None:
            return "Bike not found", 404

        moto_active = MotosModel.is_active(bikeid)

        try:
            if user.availableMoney > 5:
                if moto_active is True:
                    new_rent = BookingModel(userid, bikeid, None, None, None)
                    new_rent.startDate = datetime.now()
                    MotosModel.change_status(bikeid)

                    new_rent.save_to_db()

                    return {"new_rent": new_rent.json()}, 201
                return "Moto selected is not active", 400
            return "Not money enough", 400
        except:
            return "Something went wrong", 500

    def put(self):

        data = Booking.parser.parse_args()

        userid = data['userid']
        bikeid = data['bikeid']

        user = AccountsModel.find_by_id(userid)
        bike = MotosModel.find_by_id(bikeid)

        if user is None:
            return "User not found", 404
        if bike is None:
            return "Bike not found", 404

        try:
            admin_user = AccountsModel.find_by_username('admin')

            if admin_user:
                book = BookingModel.finalize_book(userid, bikeid)
                if book is None:
                    return "No renting found", 404
                MotosModel.change_status(bikeid)

                admin_user.availableMoney += book.price
                user.availableMoney -= book.price

                return {"finalized_rent": book.json()}, 201
            return "Admin user not found", 404
        except:
            return "Something went wrong", 500



api.add_resource(Accounts, '/account/<string:username>', '/account/<int:id>', '/account')

api.add_resource(AccountsList, '/accounts')

api.add_resource(MotosList, '/bikes')
api.add_resource(Motos,'/bike','/bike/<int:id>')

api.add_resource(Login, '/login')

api.add_resource(Booking, '/rent', '/rent/<int:userid>')
api.add_resource(BookingList, '/rents')

if __name__ == '__main__':
    app.run(port=5000, debug=True)




