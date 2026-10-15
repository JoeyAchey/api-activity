import os.path
from functools import wraps
from flask import Flask, jsonify, g, request
from flask_restful import Api, Resource, reqparse
from flask_talisman import Talisman
from flask_bcrypt import Bcrypt
from api_activity.db import Database

from api_activity._constants import PROJECT_ROOT

_KEYFILE_PATH = os.path.join(PROJECT_ROOT, "MyKey.pem")
_CERTIFICATE_PATH = os.path.join(PROJECT_ROOT, "MyCertificate.crt")

def get_db():
    if "db" not in g:
        g.db = Database()
    return g.db

def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = request.authorization

        if auth is None:
            return {"message": "Authentication required"}, 401

        if auth.type != "basic" or not auth.username or not auth.password:
            return {"message": "Invalid credentials"}, 401

        db = get_db()
        hashed_pwd = db.get_password(auth.username)

        valid = (
            hashed_pwd is not None
            and Bcrypt().check_password_hash(hashed_pwd, auth.password)
        )

        if not valid:
            return {"message": "Invalid credentials"}, 401

        g.username = auth.username
        return func(*args, **kwargs)

    return wrapper

class Hello(Resource):
    def get(self):
        return jsonify({"message": "Hello World!"})

class Square(Resource):
    def get(self, num):
        return jsonify({
            "Shape": __class__.__name__,
            "Area": num * num
        })

class Echo(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('arg1', type=str, location='args')
        parser.add_argument('arg2', type=str, location='args')
        arguments = parser.parse_args()
        return jsonify(arguments)

class Register(Resource):
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "username",
            type=str,
            required=True,
            location="json",
            help="Username is required",
        )
        parser.add_argument(
            "password",
            type=str,
            required=True,
            location="json",
            help="Password is required",
        )
        arguments = parser.parse_args()
        username = arguments["username"]
        password = arguments["password"]

        hashed_pwd = Bcrypt().generate_password_hash(password).decode("utf-8")

        db = get_db()
        if db.add_user(username, hashed_pwd):
            return {"message": f"User {username} registered successfully"}, 201

        return {"message": f"User {username} already exists"}, 409

class Profile(Resource):
    @auth_required
    def get(self):
        return jsonify({"message": f"Hello, {g.username}!"})

class Secret(Resource):
    @auth_required
    def get(self):
        return jsonify({
            "message": f"{g.username}, you accessed the secret endpoint!"
        })

def init_api(app: Flask) -> None:
    api = Api(app)
    api.add_resource(Hello, "/")
    api.add_resource(Square, "/square/<int:num>")
    api.add_resource(Echo, "/echo")
    api.add_resource(Register, "/register")
    api.add_resource(Profile, "/profile")
    api.add_resource(Secret, "/secret")

def create_app() -> Flask:
    app = Flask(__name__)
    app.config["PREFERRED_URL_SCHEME"] = "https"
    Talisman(app, force_https=True)
    init_api(app)

    @app.teardown_appcontext
    def close_db(exception):
        db = g.pop("db", None)
        if db is not None:
            db.conn.close()

    return app


def run_app(debug: bool = True, with_ssl: bool = True) -> None:
    ssl_context = (_CERTIFICATE_PATH, _KEYFILE_PATH) if with_ssl else None
    create_app().run(debug=debug, ssl_context=ssl_context)


if __name__ == "__main__":
    run_app()