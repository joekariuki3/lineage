#!/usr/bin/python3
import os
from flask import Flask, url_for, render_template, flash, redirect, request, make_response, jsonify
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, Family, Member, User, Event, Relationship
from forms import RegisterForm, LoginForm, EditProfileForm, CreateFamilyForm,AddMemberForm, AddMemberSpouseForm, AddMemberChildForm, updateMemberForm

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
        flash(f'{new_family.name} added Successfully', 'success')
        # add root member
        add_root(new_family.family_id, memberForm)
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
# Add root member
def add_root(family_id, memberForm={}):
    if not memberForm == {}:
        form = memberForm
        newMember = Member(first_name = form.first_name.data,
                           last_name = form.last_name.data,
                           birthdate = form.birthdate.data,
                           gender = form.gender.data,
                           root=True,
                           family_id = family_id,
                           alive = eval(form.alive.data),
                           deathdate = form.deathdate.data,
                           )
        db.session.add(newMember)
        db.session.commit()
        flash(f'{newMember.first_name} {newMember.last_name} added as a root Member', 'success')
        return redirect(url_for('index'))
    flash('Something went wrong Root member not Added', 'danger')
    return redirect(url_for('create_family'))

# add spouse
@app.route('/member/<member_id>/spouse', methods=['GET', 'POST'])
@login_required
def add_spouse(member_id):
    form = AddMemberSpouseForm()
    member1 = Member.query.filter_by(member_id=member_id).first()
    family_id = member1.family_id
    title = f'Adding spouse of {member1.first_name} {member1.last_name}'
    if form.validate_on_submit():
        newMember = Member(first_name = form.first_name.data,
                           last_name = form.last_name.data,
                           birthdate = form.birthdate.data,
                           gender = form.gender.data,
                           root=False,
                           family_id = family_id,
                           alive = eval(form.alive.data),
                           deathdate = form.deathdate.data,
                           )
        db.session.add(newMember)
        db.session.commit()
        flash(f'{newMember.first_name} added as spouse to {member1.first_name} {member1.last_name}', 'success')
        add_relationship(member1.member_id, newMember.member_id, form.relationship.data)
        return redirect(url_for('index'))
    return render_template('add_member.html', title=title, form=form, families=current_user.families, member1=member1)

# add child
@app.route('/member/<member_id>/<spouse_id>/child', methods=['GET', 'POST'])
@login_required
def add_child(member_id, spouse_id):
    form = AddMemberChildForm()
    father = ''
    mother = ''
    member1 = Member.query.filter_by(member_id=member_id).first()
    spouse = Member.query.filter_by(member_id=spouse_id).first()
    if member1.gender == 'Male':
        father = member1
        mother = spouse
    else:
        mother = member1
        father = spouse
    family_id = member1.family_id
    if form.validate_on_submit():
        newMember = Member(first_name = form.first_name.data,
                           last_name = form.last_name.data,
                           birthdate = form.birthdate.data,
                           gender = form.gender.data,
                           root=False,
                           family_id = family_id,
                           alive = eval(form.alive.data),
                           deathdate = form.deathdate.data,
                           father = father.member_id,
                           mother = mother.member_id
                           )
        db.session.add(newMember)
        db.session.commit()
        flash(f'{newMember.first_name} {newMember.last_name} added as child to {member1.first_name} {member1.last_name} and {spouse.first_name} {spouse.last_name}', 'success')
        add_relationship(spouse.member_id, newMember.member_id, form.relationship.data)
        return redirect(url_for('index'))
    return render_template('add_member.html', title='Add child', form=form, families=current_user.families, member1=member1)

# old add
# @app.route('/member', methods=['GET', 'POST'])
# @app.route('/member/<member1_id>', methods=['GET', 'POST'])
# @login_required
# def add_member(f_id='', memberForm={}, member1_id=''):
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

# member profile
@app.route('/member/<member_id>', methods=['GET'])
@login_required
def member_profile(member_id):
    member = Member.query.filter_by(member_id=member_id).first()
    family_id = member.family_id
    family_members = Member.query.filter_by(family_id=family_id).all()
    family_members = [ family_member for family_member in family_members if not family_member.member_id == member.member_id]

    # get sibling
    siblings = [ person for person in family_members if person.mother and person.mother == member.mother]

    # get children
    childrenMother = Member.query.filter_by(mother=member_id).all()
    childrenFather = Member.query.filter_by(father=member_id).all()
    children = []
    if childrenFather:
        children = childrenFather
    elif childrenMother:
        children = childrenMother

    # get spouse
    spousesMember1 = Relationship.query.filter_by(member_id_1=member.member_id).filter_by(relationship_type='spouse').all()
    spousesMember2 = Relationship.query.filter_by(member_id_2=member.member_id).filter_by(relationship_type='spouse').all()
    print(spousesMember1)
    print(spousesMember2)
    allSpouses = []
    for spouse in spousesMember1:
        if not spouse.member_id_1 == member_id:
            memberSpouse = Member.query.filter_by(member_id=spouse.member_id_2).first()
            allSpouses.append(memberSpouse)
    for spouse in spousesMember2:
        if not spouse.member_id_2 == member_id:
            memberSpouse = Member.query.filter_by(member_id=spouse.member_id_1).first()
            allSpouses.append(memberSpouse)

    return render_template('member_profile.html', title=f'{member.first_name} information ',
                           member=member,
                           family_members=family_members,
                           siblings=siblings,
                           spouses=allSpouses,
                           children=children)


# update member
@app.route('/update_member/<member_id>', methods=['GET', 'POST'])
@login_required
def update_member(member_id):
    form = updateMemberForm()
    member = Member.query.filter_by(member_id=member_id).first()

    form.gender.data = member.gender
    form.alive.data = str(member.alive)
    if form.validate_on_submit():
        member.first_name = form.first_name.data
        member.last_name = form.last_name.data
        member.birthdate = form.birthdate.data
        member.gender = form.gender.data
        member.deathdate = form.deathdate.data
        member.alive = eval(form.alive.data)
        db.session.commit()
        flash(f'{member.first_name} changes have been Updated.', 'success')
        return redirect(url_for('member_profile', member_id=member.member_id))
    return render_template('update_member.html', title=f'update {member.first_name} information ',
                           form=form, member=member)

# API call retrieve nuclear family of member with id passed
# return spouses
@app.route('/member/spouses', methods=['POST', 'GET'])
@login_required
def get_spouse():
    data = request.get_json()
    if not data:
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    elif "member1_id" not in data:
        return make_response(jsonify({"error": "Missing member1_id"}), 400)
    spousesList = []
    spouses = Relationship.query.filter_by(member_id_1=int(data['member1_id']), relationship_type='spouse').all()
    for spouse in spouses:
        spouse_member = Member.query.filter_by(member_id=spouse.member_id_2).first()
        spouse_member = spouse_member.__dict__
        del spouse_member['_sa_instance_state']
        spousesList.append(spouse_member)
    response =  make_response(jsonify(spousesList), 200)
    return response

# return children
@app.route('/member/children', methods=['POST', 'GET'])
@login_required
def get_children():
    data = request.get_json()
    if not data:
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    elif "member1_id" not in data:
        return make_response(jsonify({"error": "Missing member1_id"}), 400)
    elif "spouse_id" not in data:
        return make_response(jsonify({"error": "Missing spouse_id"}), 400)
    member1 = Member.query.filter_by(member_id=data['member1_id']).first()
    spouse = Member.query.filter_by(member_id=data['spouse_id']).first()
    if member1.gender == 'Male':
        father = member1
        mother = spouse
    else:
        mother = member1
        father = spouse
    childrenList = []
    fatherMotherRelation = Relationship.query.filter_by(member_id_1=member1.member_id, member_id_2=spouse.member_id).first()
    fatherMotherRelation = fatherMotherRelation.relationship_type
    if fatherMotherRelation == 'spouse':
        children = Relationship.query.filter_by(member_id_1=spouse.member_id, relationship_type='child').all()
        for child in children:
            child_member = Member.query.filter_by(member_id=child.member_id_2).first()
            child_member = child_member.__dict__
            del child_member['_sa_instance_state']
            childrenList.append(child_member)
        response =  make_response(jsonify(childrenList), 200)
        return response

# @app.route('/member/nuclear', methods=['POST', 'GET'])
# @login_required
# def get_nuclear():
    data = request.get_json()
    if not data:
        return make_response(jsonify({"error": "Not a JSON"}), 400)
    elif "member1_id" not in data:
        return make_response(jsonify({"error": "Missing member1_id"}), 400)
    nuclear_family = {"spouses": [], "children": []}
    spouses = Relationship.query.filter_by(member_id_1=int(data['member1_id']), relationship_type='spouse').all()
    children = Relationship.query.filter_by(member_id_1=int(data['member1_id']), relationship_type='child').all()
    for spouse in spouses:
        spouse_member = Member.query.filter_by(member_id=spouse.member_id_2).first()
        spouse_member = spouse_member.__dict__
        del spouse_member['_sa_instance_state']
        nuclear_family['spouses'].append(spouse_member)
    for child in children:
        child_member = Member.query.filter_by(member_id=child.member_id_2).first()
        child_member = child_member.__dict__
        del child_member['_sa_instance_state']
        nuclear_family['children'].append(child_member)
    response =  make_response(jsonify(nuclear_family), 200)
    return response


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