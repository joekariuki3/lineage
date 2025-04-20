from itsdangerous import URLSafeTimedSerializer
from config import Config

auth_s = URLSafeTimedSerializer(Config.SECRET_KEY, salt=Config.SALT)
