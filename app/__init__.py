from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from flask import Flask
from flask_restful import Api
from app.setup.settings import TwitterSettings
from app.admin import admin as Admin
from app.live import live as Live
from app.setup.database import db
from app.messages import response_errors as Err
from app.models.admin import AdminModel
from app.resources.fortauth import FortAuth


def create_app():
    # Create a Flask Application
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
        instance_relative_config=True,
    )

    app.register_blueprint(Admin, url_prefix="/admin")
    app.register_blueprint(Live, url_prefix="/live")

    # Flask configurations
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"sqlite:///{TwitterSettings.get_instance().database_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.secret_key = TwitterSettings.get_instance().jwt_secret_key
    api = Api(app)

    # SQLAlchemy configurations
    db.app = app
    db.init_app(app)
    app.app_context().push()
    db.create_all()

    return app, api


app, api = create_app()

# JWT Configurations
jwt = JWTManager(app)

# Socket IO
socketio = SocketIO(app, cors_allowed_origins="*")

# Other imports
from app.resources.tweets import (
    Tweets,
    TweetSearch,
    AuthorSearch,
    DateSearch,
    LocationSearch,
    SourceSearch,
)

# Creates default admins and insert in db
for admin in TwitterSettings.get_instance().super_admins:
    admin = AdminModel(admin["email"], admin["username"], admin["password"])
    admin.insert()

# Error handlers
@app.errorhandler(404)  # Handling HTTP 404 NOT FOUND
def page_not_found(e):
    return Err.ERROR_NOT_FOUND


# API Routes
api.add_resource(Tweets, "/api/tweets")
api.add_resource(TweetSearch, "/api/tweets/tweet")
api.add_resource(SourceSearch, "/api/tweets/source")
api.add_resource(AuthorSearch, "/api/tweets/author")
api.add_resource(DateSearch, "/api/tweets/date")
api.add_resource(LocationSearch, "/api/tweets/location")
api.add_resource(FortAuth, "/api/fortauth")

# Start the app
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0")

