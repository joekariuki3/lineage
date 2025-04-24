from . import bp
from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.extensions import db
from .forms import EditProfileForm
from .services import update_user, get_user


@bp.route('/user/profile')
@login_required
def user_profile():
    url_root = request.url_root
    return render_template('profile.html', title='User_Profile', url_root=url_root)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        code, message, category = update_user(current_user, name=form.name.data, email=form.email.data)

        if code != 200:
            flash(message, category)
            return render_template('edit_profile.html', title='Edit Profile', form=form)

        flash(message, category)
        return redirect(url_for('user.user_profile'))

    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@bp.route('/user/verify_email/<user_id>')
@login_required
def verify_email(user_id):
    user = get_user(id=user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('user.user_profile'))

    sendEmailVerificationLink(user)
    return redirect(url_for('user.user_profile'))

@bp.route('/verify_email/<token>')
def update_verify_email(token):
    data = auth_s.loads(token)
    user_id = data["user_id"]

    if user_id:
        user = get_user(id=user_id)
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('auth.login'))

        code, message, category = update_user(user, emailVerify=True)
        if code != 200:
            flash(message, category)
            return redirect(url_for('auth.login'))
        flash(message, category)
    return redirect(url_for('auth.login'))
