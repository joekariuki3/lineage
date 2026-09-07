from flask import Flask

from config import DevelopmentConfig


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)

    # Load configuration
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
    from .auth import auth_bp
    from .error import error_bp
    from .event import event_bp
    from .family import family_bp
    from .link import link_bp
    from .main.routes import main_bp
    from .member import member_bp
    from .user import user_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(family_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(member_bp)
    app.register_blueprint(error_bp)
    app.register_blueprint(link_bp)

    with app.app_context():
        db.create_all()

    return app