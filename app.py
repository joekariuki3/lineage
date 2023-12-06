#!/usr/bin/python3
import os
from flask import Flask, url_for, render_template, flash, redirect, request, make_response, jsonify
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, Family, Member, User, Event, Relationship, Link
from forms import RegisterForm, LoginForm, EditProfileForm, CreateFamilyForm,AddMemberForm, AddMemberSpouseForm, AddMemberChildForm, updateMemberForm, AddEventForm
from datetime import datetime
from itsdangerous import URLSafeSerializer
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

secret_key = os.environ.get('SECRET_KEY')
auth_s = URLSafeSerializer(secret_key, "auth")


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

# Home
@app.route('/<family_id>')
@app.route('/')
def home(family_id=''):
    families = []
    if not family_id == '':
        try:
            data = auth_s.loads(family_id)
            print(data)
            family_id = data["family_id"]
            if family_id:
                families = Family.query.filter_by(family_id=family_id).all()
        except Exception as e:
            pass
    return render_template('index.html', title="Lineage Home", families=families)

@app.route('/family/<family_id>')
@app.route('/family')
def index(family_id=0):
    families = []
    if not family_id == 0:
        families = Family.query.filter_by(family_id=family_id).all()
    elif current_user.is_authenticated:
        families = Family.query.filter_by(user_id=current_user.user_id).all()
    return render_template('family.html', families=families)

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

#create link for members
@app.route('/create_link/<family_id>', methods=['POST', 'GET'])
@login_required
def create_link(family_id):
    links = Link.query.filter_by(family_id=family_id).all()
    if len(links) < 1:
        # create new link
        token = auth_s.dumps({"family_id": family_id})
        newLink = Link(link=token, family_id=family_id)
        db.session.add(newLink)
        db.session.commit()
        url_root = request.url_root
        flash('Link created', 'success')
        return render_template('profile.html', title='User_Profile', url_root=url_root)
    flash('You already have a link. Delete the current one to create a new one', 'warning')
    return render_template('profile.html', title='User_Profile')
# delete link
@app.route('/delete_link/<link_id>')
@login_required
def delete_link(link_id):
    link = Link.query.filter_by(link_id=link_id).first()
    if link:
        db.session.delete(link)
        db.session.commit()
        flash('Link deleted', 'success')
        return redirect(url_for('user_profile'))
    return redirect(url_for('user_profile'))
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
@app.route('/create-family', methods=['GET', 'POST'])
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
        return redirect(url_for('user_profile'))
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

# member profile
@app.route('/member/<member_id>', methods=['GET'])
# @login_required
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

# API call
# return spouses
@app.route('/member/spouses', methods=['POST', 'GET'])
# @login_required
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
    if current_user.is_authenticated:
        login = {'authenticated': True}
    else:
        login = {'authenticated': False}
    response =  make_response(jsonify(spousesList, login), 200)
    return response

# return children
@app.route('/member/children', methods=['POST', 'GET'])
# @login_required
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
        if current_user.is_authenticated:
            login = {'authenticated': True}
        else:
            login = {'authenticated': False}
        response =  make_response(jsonify(childrenList, login), 200)
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

# add event
@app.route('/event/', methods=['POST', 'GET'])
@login_required
def add_event():
    form = AddEventForm()
    if form.validate_on_submit():
        date = form.date.data
        name = form.name.data
        location = form.location.data
        description = form.description.data
        # get family id
        family_id = request.form.get('family')
        newEvent = Event(event_date=date,
                     event_name=name,
                     location=location,
                     description=description,
                     family_id=family_id)
        db.session.add(newEvent)
        db.session.commit()
        flash(f'{newEvent.event_name} added Successfully', 'success')
        return(redirect(url_for('get_events', family_id=newEvent.family_id)))
    return render_template('add_event.html', title='Add Event', form=form)

# get All events
@app.route('/event/<family_id>', methods=['POST', 'GET'])
# @login_required
def get_events(family_id):
    currentTime = datetime.now()
    upcomingEvents = Event.query.order_by(Event.event_date.asc()).filter_by(family_id=family_id).filter(Event.event_date>=currentTime ).all()
    pastEvents = Event.query.order_by(Event.event_date.asc()).filter_by(family_id=family_id).filter(Event.event_date<=currentTime ).all()
    return render_template('events.html', upcomingEvents=upcomingEvents, pastEvents=pastEvents)

# delete an Event
@app.route('/delete/event/<event_id>')
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    user_ids = [family.family_id for family in current_user.families]
    if event.family_id in user_ids:
        db.session.delete(event)
        db.session.commit()
        flash(f'{event.event_name} Deleted successfully', 'info')
        return redirect(url_for('get_events', family_id=event.family_id))
    flash('You dont have permission to delete this event', 'warning')
    return redirect(url_for('get_events', family_id=event.family_id))

# edit an Event
@app.route('/edit/event/<event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    form = AddEventForm()
    user_ids = [family.family_id for family in current_user.families]
    if form.validate_on_submit() and event.family_id in user_ids:
        event.event_date = form.date.data
        event.event_name = form.name.data
        event.location = form.location.data
        event.description = form.description.data
        db.session.commit()
        flash(f'{event.event_name} details Updated', 'success')
        return redirect(url_for('get_events', family_id=event.family_id))
    form.description.data = event.description
    return render_template('edit_event.html', title='Update Event details', event=event, form=form)

# executed as main run
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables based on models
    app.run(debug=True, host='0.0.0.0')