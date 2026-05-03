from flask import Flask, request, redirect, url_for, flash
from models import db, User, PetOwner, Pet, Appointment
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vetcare.db'
app.config['SECRET_KEY'] = 'dev-secret-key-123'

db.init_app(app)

with app.app_context():
    db.create_all()
    print("Database woooh!")

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

if __name__ == '__main__':
    app.run(debug=True)