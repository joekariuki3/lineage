from . import bp
from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.extensions import db
from .forms import EditProfileForm


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
        current_user.name = form.name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('user.user_profile'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@bp.route('/user/verify_email/<user_id>')
@login_required
def verifyEmail(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    sendEmailVerificationLink(user)
    return redirect(url_for('user.user_profile'))

@bp.route('/verify_email/<token>')
def UpdateVerifyEmail(token):
    try:
        data = auth_s.loads(token)
        user_id = data["user_id"]
        if user_id:
            user = User.query.filter_by(user_id=user_id).first()
            user.emailVerify = True
            db.session.commit()
            flash('Email verified', 'success')
    except Exception as e:
        pass
    return redirect(url_for('auth.login'))
