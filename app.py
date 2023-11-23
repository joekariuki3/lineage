#!/usr/bin/python3
import os
from flask import Flask, url_for, render_template, flash, redirect, request
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, Family, Member, User, Event, Relationship
from forms import RegisterForm, LoginForm, EditProfileForm, CreateFamilyForm,AddMemberForm

app = Flask(__name__)
login = LoginManager(app)
login.login_view = 'login'

# Set the secret key using an environment variable
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Set the database URI using an environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('LINEAGE_DATABASE_URI')

# Silence the deprecation warning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Flask extensions
db.init_app(app)
# create an instance
migrate = Migrate()
#initiate migration
migrate.init_app(app, db)


# handle errors
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# load login user
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# secret page
@app.route('/secret')
@login_required
def secret():
    return render_template('secret.html')
# Home
@app.route('/')
def index():
    families = []
    if current_user.is_authenticated:
        families = Family.query.filter_by(user_id=current_user.user_id)
    return render_template('index.html', families=families)

# Register
@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
         return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration was a success Login Now', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page:
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form)

# logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# userProfile
@app.route('/user/profile')
@login_required
def user_profile():
    return render_template('profile.html', title='User_Profile')

# edit profile
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('user_profile'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

# create family
@app.route('/family', methods=['GET', 'POST'])
@login_required
def create_family():
    form = CreateFamilyForm()
    memberForm = AddMemberForm()
    if form.validate_on_submit() and memberForm.validate_on_submit():
        family_name = form.name.data
        new_family = Family(name=family_name, user_id=current_user.user_id)
        db.session.add(new_family)
        db.session.commit()
        flash('Family added Successfully', 'success')
        # add root member
        add_member(new_family.family_id, memberForm)
        return redirect(url_for('index'))
    return render_template('create_family.html', title='Create Family', form=form, memberForm=memberForm)

# delete a Family
@app.route('/family/delete/<id>')
@login_required
def delete_family(id):
    family = Family.query.filter_by(family_id=id).first()
    if current_user.user_id == family.user_id:
        db.session.delete(family)
        db.session.commit()
        flash('Family deleted successful', 'success')
    else:
        flash('You are not allowed to delete this family', 'info')
    return redirect(url_for('user_profile'))

#Add family member
@app.route('/member', methods=['GET', 'POST'])
@app.route('/member/<member1_id>', methods=['GET', 'POST'])
@login_required
def add_member(f_id='', memberForm={}, member1_id=''):
    root = False
    member1 = ''
    if not member1_id == '':
        member1 = Member.query.filter_by(member_id=member1_id).first()
    if f_id == '':
        f_id = request.form.get('family')
    if not memberForm == {}:
        form = memberForm
        root = True
    form = AddMemberForm()
    if form.validate_on_submit():
        a_live = False
        if form.alive.data == 'Yes':
            a_live = True
        newMember = Member(first_name = form.first_name.data,
                           last_name = form.last_name.data,
                           birthdate = form.birthdate.data,
                           gender = form.gender.data,
                           root=root,
                           family_id = f_id,
                           alive = a_live,
                           deathdate = form.deathdate.data,
                           )
        db.session.add(newMember)
        db.session.commit()
        flash('Member added Successfully', 'success')
        add_relationship(member1.member_id, newMember.member_id, form.relationship.data)
        return redirect(url_for('index'))
    return render_template('add_member.html', title='Add member', form=form, families=current_user.families, member1=member1)

# relationship
def add_relationship(member1_id, member2_id, relationship_type):
    new_relationship = Relationship(member_id_1=member1_id, member_id_2=member2_id, relationship_type=relationship_type)
    db.session.add(new_relationship)
    db.session.commit()

# executed as main run
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables based on models
    app.run(debug=True, host='0.0.0.0')