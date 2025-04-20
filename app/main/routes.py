from flask import render_template
from flask_login import current_user
from app.models.family import Family
from . import bp
from app.utils import auth_s

@bp.route('/<family_id>')
@bp.route('/')
def index(family_id=''):
    families = []
    if family_id:
        try:
            data = auth_s.loads(family_id)
            family_id = data["family_id"]
            if family_id:
                families = Family.query.filter_by(family_id=family_id).all()
        except Exception as e:
            pass
    return render_template('index.html', title="Lineage Home", families=families)