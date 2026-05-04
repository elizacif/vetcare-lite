from flask import Flask, request, redirect, url_for, flash
from models import db, User, PetOwner, Pet, Appointment
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import requests

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vetcare.db'
app.config['SECRET_KEY'] = 'dev-secret-key-123'

db.init_app(app)

with app.app_context():
    db.create_all()
    print("Database woooh!")

def get_weather_advice():
    try: 
        url = "https://api.open-meteo.com/v1/forecast?latitude=56.95&longitude=24.10&current_weather=true"
        response = requests.get(url, timeout=10)
        data = response.json()
        temp = data['current_weather']['temperature']
        
        if temp > 7:
                advice = f"It's {temp}°C. Ticks are active - use tick/flea prevention!"
        elif temp < 0:
            advice = f"It's {temp}°C. Careful of road salt causing irritation on pet paws!"
        else:
            advice = f"It's {temp}°C. Standard health checks recommended."
        return advice

    except Exception:
        return "Weather service unavailable. Ensure pets are up to date on vaccinations."


@app.route('/')
def dashboard():

    vet_tip = get_weather_advice()

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
        
    return output

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(username=request.form.get('username'))
        user.set_password(request.form.get('password'))
        db.session.add(user)
        db.session.commit()
        return "User created successfully! <a href='/'>Go to Dashboard</a>"
    return '''
        <form method="POST">
            <input name="username" placeholder="Username" required>
            <input name="password" type="password" placeholder="Password" required>
            <button type="submit">Register Staff</button>
        </form>
    '''

@app.route('/owner/add', methods=['GET', 'POST'])
def add_owner():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')

        if name and phone:
            try:
                new_owner = PetOwner(name=name, phone=phone, email=email)
                db.session.add(new_owner)
                db.session.commit()
                return redirect(url_for('dashboard'))
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



@app.route('/owner/delete/<int:id>')
def delete_owner(id):
    owner = PetOwner.query.get_or_404(id)
    try:
        db.session.delete(owner)
        db.session.commit()
        return redirect(url_for('dashboard'))
    except Exception as e:
        db.session.rollback()
        return f"Error deleting owner: {e}"            
    

@app.route('/owner/edit/<int:id>', methods=['GET', 'POST'])
def edit_owner(id):
    owner = PetOwner.query.get_or_404(id)
    
    if request.method == 'POST':
        owner.name = request.form.get('name')
        owner.phone = request.form.get('phone')
        owner.email = request.form.get('email')
        
        try:
            db.session.commit()
            return redirect(url_for('dashboard'))
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

@app.route('/pet/add/<int:owner_id>', methods=['GET', 'POST'])
def add_pet(owner_id):
    owner = PetOwner.query.get_or_404(owner_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        species = request.form.get('species')
        breed = request.form.get('breed')
        
        new_pet = Pet(name=name, species=species, breed=breed, owner_id=owner.id)
        db.session.add(new_pet)
        db.session.commit()
        return redirect(url_for('dashboard'))
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

@app.route('/pet/delete/<int:id>')
def delete_pet(id):
    pet = Pet.query.get_or_404(id)
    db.session.delete(pet)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/pet/edit/<int:id>', methods=['GET', 'POST'])
def edit_pet(id):
    pet = Pet.query.get_or_404(id)
    
    if request.method == 'POST':
        pet.name = request.form.get('name')
        pet.species = request.form.get('species')
        pet.breed = request.form.get('breed')
        
        try:
            db.session.commit()
            return redirect(url_for('dashboard'))
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

@app.route('/appointment/add/<int:pet_id>', methods=['GET', 'POST'])
def add_appointment(pet_id):
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
            return redirect(url_for('dashboard'))

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)