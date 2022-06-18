from os import environ

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = environ.get("SQLALCHEMY_DATABASE_URI")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_size": 10,
        "max_overflow": 10
    }

    __import__("app.models")
    db.init_app(app=app)
    migrate.init_app(app=app, db=db)

    from . import key
    app.config['SECRET_KEY'] = key.secret_key()

    from . import views
    for view in views.__all__:
        app.register_blueprint(getattr(getattr(views, view), "bp"))

    from flask import url_for
    from flask import redirect
    from app.utils import set_message
    from app.const import ERROR

    def on_error(error_code: int):
        message_id = set_message(message=ERROR[error_code])
        return redirect(url_for("index.index", error=message_id))

    for code in ERROR:
        app.register_error_handler(
            code_or_exception=code,
            f=lambda e: on_error(error_code=e.code)
        )

    return app
