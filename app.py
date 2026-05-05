from flask import Flask
from models import db
from routes import main
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vetcare.db'
app.config['SECRET_KEY'] = 'super-secret-shsh'
db.init_app(app)
app.register_blueprint(main)

with app.app_context():
    db.create_all()
    print("Database woooh!")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)