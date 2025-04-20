from flask import Blueprint

bp = Blueprint('member', __name__)

from app.member import routes