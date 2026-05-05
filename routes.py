from flask import Blueprint, request, redirect, url_for, session, flash
from models import db, User, PetOwner, Pet, Appointment
from utils import get_weather_advice
from werkzeug.security import generate_password_hash

main = Blueprint('main', __name__)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            return "Error: Username already exists.", 400

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return "Account created. Pending aprooval. <a href='/login'>Go to Login</a>"
    return '''
        <h1>Register</h1>
        <form method="post">
            <input name="username" placeholder="Username" required><br>
            <input name="password" type="password" placeholder="Password" required><br>
            <button type="submit">Request Access</button>
        </form>
    '''

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('main.dashboard'))
    
        return "Invalid credentials. <a href='/login'>Try again</a>"

    return '''
        <h1>Login</h1>
        <form method="post">
            <input name="username" placeholder="Username" required><br>
            <input name="password" type="password" placeholder="Password" required><br>
            <button type="submit">Login</button>
        </form>
        <p>New staff? <a href="/register">Register here</a></p>
    '''

@main.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.login'))

@main.route('/admin/users')
def admin_panel():
    curr_user = User.query.get(session.get('user_id'))
    if not curr_user or curr_user.username != 'admin':
        return "Admin only."

    all_users = User.query.all()
    res = "MANAGE USERS:"
    
    for u in all_users:
        status = "OK" if u.is_approved else "PENDING"
        line = f"User: {u.username} [{status}]"
        
        if not u.is_approved:
            url = url_for('main.approve_user', user_id=u.id)
            line += f" <a href='{url}'>[APPROVE]</a>"

    return "<br><a href='/'>Back</a>"

@main.route('/admin/approve/<int:user_id>')
def approve_user(user_id):
    curr_user = User.query.get(session.get('user_id'))
    if not curr_user or curr_user.username != 'admin':
        return "Unauthorized"

    u = User.query.get_or_404(user_id)
    u.is_approved = True
    db.session.commit()
    return redirect(url_for('main.admin_panel'))


@main.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])
    
    if user.username != 'admin' and not user.is_approved:
        return "<h1>Access Pending</h1>"

    admin_tools = ""

    if user.username == 'admin':
        admin_tools = f"<a href='/admin/users'>Manage User Approvals</a>"


    vet_tip = get_weather_advice()

    admin_tools = ""
    if user.username == 'admin':
        admin_tools = f"<a href='{url_for('main.admin_panel')}'>Approve New Users</a>"

    output = f"""
        <div margin-bottom:20px;">
            Daily Clinic Alert: {vet_tip}
        </div>
    """

    search_query = request.args.get('search', '') 
    
    if search_query:
        owners = PetOwner.query.filter(
            (PetOwner.name.contains(search_query)) | 
            (PetOwner.phone.contains(search_query))
        ).all()
    else:
        owners = PetOwner.query.all()

    output += "<h1>VetCare Lite Dashboard</h1>"
    output += f'''
        <form method="GET" action="/">
            <input type="text" name="search" placeholder="Search name or phone..." value="{search_query}">
            <button type="submit">Search</button>
            <a href="/">Clear</a>
        </form>
        <br>
        <a href="/owner/add">[+ Add New Owner]</a><hr>
    '''    
    for owner in owners:
        output += f"""
            <div>
                <strong>{owner.name}</strong> ({owner.phone}) 
                <a href='/owner/edit/{owner.id}'>[Edit]</a> 
                <a href='/owner/delete/{owner.id}' style='color:red;'>[Delete]</a>
                <ul style="margin-top: 10px;">
        """
        
        for pet in owner.pets:
            output += f"""
                <li>
                    {pet.name} ({pet.species}) 
                    [<a href='/appointment/add/{pet.id}'>Book</a>] 
                    [<a href='/pet/edit/{pet.id}'>Edit</a>] 
                    [<a href='/pet/delete/{pet.id}' style='color:red;'>Delete</a>]
                
            """
            if pet.appointments:
                output += "<ul>"
                for appt in pet.appointments:
                    pretty_date = appt.datetime.strftime('%d.%m.%Y %H:%M')
                    output += f"<li>{pretty_date} - {appt.reason}</li>"
                output += "</ul>"
            
            output += "</li>"
            
        output += f"<li><a href='/pet/add/{owner.id}'>+ Add Pet</a></li>"
        output += "</ul></div>"
    output += f"</ul><br><br><a href='{url_for('main.logout')}'>Logout</a>"
    
    return output



@main.route('/owner/add', methods=['GET', 'POST'])
def add_owner():
    if 'user_id' not in session or not User.query.get(session['user_id']).is_approved:
        return "Unauthorized"

    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')

        if name and phone:
            try:
                new_owner = PetOwner(name=name, phone=phone, email=email)
                db.session.add(new_owner)
                db.session.commit()
                return redirect(url_for('main.dashboard'))
            except Exception as e:
                db.session.rollback()
                return f"<h1>Error</h1><p>{e}</p><a href='/owner/add'>Try again</a>"    
    return '''
        <form method="POST">
            <input type="text" name="name" placeholder="Owner Name" required>
            <input type="text" name="phone" placeholder="Phone" required>
            <input type="email" name="email" placeholder="Email">
            <button type="submit">Save Owner</button>
        </form>
    '''



@main.route('/owner/delete/<int:id>')
def delete_owner(id):
    if 'user_id' not in session or not User.query.get(session['user_id']).is_approved:
        return "Unauthorized"

    owner = PetOwner.query.get_or_404(id)
    try:
        db.session.delete(owner)
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        db.session.rollback()
        return f"Error deleting owner: {e}"            
    

@main.route('/owner/edit/<int:id>', methods=['GET', 'POST'])
def edit_owner(id):
    if 'user_id' not in session or not User.query.get(session['user_id']).is_approved:
        return "Unauthorized"

    owner = PetOwner.query.get_or_404(id)
    
    if request.method == 'POST':
        owner.name = request.form.get('name')
        owner.phone = request.form.get('phone')
        owner.email = request.form.get('email')
        
        try:
            db.session.commit()
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            return f"<h1>Update Error</h1><p>{str(e)}</p><a href='/owner/edit/{id}'>Try again</a>"

    return f'''
        <h1>Edit Owner: {owner.name}</h1>
        <form method="POST">
            <input type="text" name="name" value="{owner.name}" required>
            <input type="text" name="phone" value="{owner.phone}" required>
            <input type="email" name="email" value="{owner.email}">
            <button type="submit">Update Info</button>
        </form>
        <br><a href="/">Cancel</a>
    '''

@main.route('/pet/add/<int:owner_id>', methods=['GET', 'POST'])
def add_pet(owner_id):
    if 'user_id' not in session or not User.query.get(session['user_id']).is_approved:
        return "Unauthorized"
    owner = PetOwner.query.get_or_404(owner_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        species = request.form.get('species')
        breed = request.form.get('breed')
        
        new_pet = Pet(name=name, species=species, breed=breed, owner_id=owner.id)
        db.session.add(new_pet)
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    return f'''
        <h1>Add Pet for {owner.name}</h1>
        <form method="POST">
            <input type="text" name="name" placeholder="Pet Name" required>
            <input type="text" name="species" placeholder="Species (e.g. Dog)">
            <input type="text" name="breed" placeholder="Breed">
            <button type="submit">Save Pet</button>
        </form>
        <br><a href="/">Cancel</a>
    '''

@main.route('/pet/delete/<int:id>')
def delete_pet(id):
    if 'user_id' not in session or not User.query.get(session['user_id']).is_approved:
        return "Unauthorized"
    pet = Pet.query.get_or_404(id)
    db.session.delete(pet)
    db.session.commit()
    return redirect(url_for('main.dashboard'))

@main.route('/pet/edit/<int:id>', methods=['GET', 'POST'])
def edit_pet(id):
    if 'user_id' not in session or not User.query.get(session['user_id']).is_approved:
        return "Unauthorized"
    pet = Pet.query.get_or_404(id)
    
    if request.method == 'POST':
        pet.name = request.form.get('name')
        pet.species = request.form.get('species')
        pet.breed = request.form.get('breed')
        
        try:
            db.session.commit()
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            return f"<h1>Error</h1><p>{e}</p>"

    return f'''
        <h1>Edit Pet: {pet.name}</h1>
        <form method="POST">
            <input type="text" name="name" value="{pet.name}" required>
            <input type="text" name="species" value="{pet.species}">
            <input type="text" name="breed" value="{pet.breed}">
            <button type="submit">Update Pet</button>
        </form>
        <br><a href="/">Cancel</a>
    '''

@main.route('/appointment/add/<int:pet_id>', methods=['GET', 'POST'])
def add_appointment(pet_id):
    if 'user_id' not in session or not User.query.get(session['user_id']).is_approved:
        return "Unauthorized"
    pet = Pet.query.get_or_404(pet_id)

    if request.method == 'POST':
        date_str = request.form.get('appt_date')
        reason = request.form.get('reason')

        try:
            clean_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            
            if clean_date < datetime.now():
                return "<h1>Error</h1><p>Insert a valid date</p><a href='javascript:history.back()'>Go Back</a>"

            new_appt = Appointment(
                datetime=clean_date, 
                reason=reason, 
                pet_id=pet.id
                )

            db.session.add(new_appt)
            db.session.commit()
            return redirect(url_for('main.dashboard'))

        except Exception as e:
            db.session.rollback()
            return f"Error: {e}"


    return f'''
        <h2>Schedule for {pet.name}</h2>
        <form method="POST">
            <label>Date and Time:</label><br>
            <input type="datetime-local" name="appt_date" required><br><br>
            
            <label>Reason:</label><br>
            <input type="text" name="reason" placeholder="Reason" required><br><br>
            
            <button type="submit">Confirm Appointment</button>
        </form>
        <a href="/">Cancel</a>
    '''