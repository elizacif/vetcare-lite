from flask import Flask, request, redirect, url_for, flash
from models import db, User, PetOwner, Pet, Appointment
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vetcare.db'
app.config['SECRET_KEY'] = 'dev-secret-key-123'

db.init_app(app)

with app.app_context():
    db.create_all()
    print("Database woooh!")

@app.route('/')
def dashboard():
    owners = PetOwner.query.all()
    output = "<h1>VetCare Lite Dashboard</h1>"
    output += "<a href='/owner/add'>[+ Add New Owner]</a><hr>"
    
    for owner in owners:
        output += f"""
            <div>
                <strong>{owner.name}</strong> ({owner.phone}) 
                <a href='/owner/edit/{owner.id}'>[Edit]</a> 
                <a href='/owner/delete/{owner.id}' style='color:red;'>[Delete]</a>
        """
        
        for pet in owner.pets:
            output += f"""
                <li>
                    {pet.name} ({pet.species}) 
                    [<a href='/appointment/add/{pet.id}'>Book</a>] 
                    [<a href='/pet/edit/{pet.id}'>Edit</a>] 
                    [<a href='/pet/delete/{pet.id}' style='color:red;'>Delete</a>]
                </li>
            """
        output += f"<li><a href='/pet/add/{owner.id}'>+ Add Pet</a></li>"
        output += "</ul></div><hr>"
        
    return output

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
    return f'''
        <h1>Add Pet for {owner.name}</h1>
        <form method="POST">
            <input type="text" name="name" placeholder="Pet Name" required>
            <input type="text" name="species" placeholder="Species (e.g. Dog)">
            <input type="text" name="breed" placeholder="Breed">
            <button type="submit">Save Pet</button>
        </form>
    '''

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
        
        if name:
            new_pet = Pet(name=name, species=species, breed=breed, owner_id=owner.id)
            db.session.add(new_pet)
            db.session.commit()
            return redirect(url_for('dashboard'))

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
        reason = request.form.get('reason')
        new_appt = Appointment(
            datetime=datetime.now(), 
            reason=reason, 
            pet_id=pet.id
        )
        db.session.add(new_appt)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return f'''
        <h1>Schedule for {pet.name}</h1>
        <form method="POST">
            <input type="text" name="reason" placeholder="Reason for visit" required>
            <button type="submit">Book Appointment</button>
        </form>
    '''

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)