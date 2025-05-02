from flask import render_template, redirect, url_for, flash, request, session
from flask_login import current_user, login_required
from . import bp
from app.models import Family, Link
from app.extensions import db
from .forms import CreateFamilyForm
from app.member.forms import MemberForm
from config import Config
from app.member.routes import add_root
from app.utils import auth_s
from app.auth.services import AuthService
from .services import FamilyService


@bp.route('/family/<family_id>')
@bp.route('/family')
def index(family_id=0):
    families = []
    if not family_id == 0:
        AuthService.set_current_family_id(family_id)

        current_family_id = session.get("current_family_id")
        if current_family_id is not None:
            data, status = FamilyService.get_family_by_id(current_family_id)
            family, message, category = data.get('data'), data.get('message'), data.get('category')
            if status != 200:
                flash(message, category)
            elif not family:
                flash(message, category)
            else:
                families = [family]

    elif current_user.is_authenticated:
        data, status = FamilyService.get_user_families(current_user.user_id)
        families, message, category = data.get('data'), data.get('message'), data.get('category')
        if status != 200:
            flash(message, category)
        elif not families:
            flash(message, category)

    return render_template('family.html', families=families)


@bp.route('/create-family', methods=['GET', 'POST'])
@login_required
def create_family():
    form = CreateFamilyForm()
    memberForm = MemberForm()

    if form.validate_on_submit() and memberForm.validate_on_submit():
        data, status = FamilyService.create_family(form.name.data, current_user.user_id)
        family, message, category = data.get('data'), data.get('message'), data.get('category')
        if status != 201:
            flash(message, category)
            return redirect(url_for('family.index'))

        add_root(family.family_id, memberForm) # To fix: use MemberService to add root member handler errors
        return redirect(url_for('family.index'))

    return render_template('create_family.html', title='Create Family', form=form, memberForm=memberForm)

@bp.route('/family/delete/<id>')
@login_required
def delete_family(id):
    family = Family.query.filter_by(family_id=id).first()
    if current_user.user_id == family.user_id:
        db.session.delete(family)
        db.session.commit()
        flash('Family deleted successful', 'success')
        return redirect(url_for('user.user_profile'))
    else:
        flash('You are not allowed to delete this family', 'info')
    return redirect(url_for('user.user_profile'))

@bp.route('/create_link/<family_id>', methods=['POST', 'GET'])
@login_required
def create_link(family_id):
    links = Link.query.filter_by(family_id=family_id).all()
    url_root = request.url_root
    if len(links) < 1:
        # create new link
        token = auth_s.dumps({"family_id": family_id})
        newLink = Link(link=token, family_id=family_id)
        db.session.add(newLink)
        db.session.commit()
        flash(f'Link created', 'success')
        return render_template('profile.html', title='User_Profile', url_root=url_root)
    flash('You already have a link. Delete the current one to create a new one', 'warning')
    return render_template('profile.html', title='User_Profile', url_root=url_root)

@bp.route('/delete_link/<link_id>')
@login_required
def delete_link(link_id):
    link = Link.query.filter_by(link_id=link_id).first()
    if link:
        db.session.delete(link)
        db.session.commit()
        flash('Link deleted', 'success')
        return redirect(url_for('user.user_profile'))
    return redirect(url_for('user.user_profile'))
