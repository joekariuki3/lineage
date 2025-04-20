from flask import Flask
from config import config_dict

def create_app(config_name='default'):
    app = Flask(__name__)

    # Load configuration
    config_class = config_dict.get(config_name)
    app.config.from_object(config_class)

    # Initialize extensions
    from .extensions import db, login_manager, mail
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)


    # Set login manager settings
    login_manager.login_view = app.config['LOGIN_VIEW']
    login_manager.login_message_category = app.config['LOGIN_MESSAGE_CATEGORY']
    #load user
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from .main.routes import bp as main_bp
    from .auth import bp as auth_bp
    from .family import bp as family_bp
    from .event import bp as event_bp
    from .user import bp as user_bp
    from .member import bp as member_bp
    from .error import bp as error_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(family_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(member_bp)
    app.register_blueprint(error_bp)

    with app.app_context():
        db.create_all()

    return app