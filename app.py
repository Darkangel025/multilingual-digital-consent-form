# app.py

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://consent_user:your_password@localhost/consent_db'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class ConsentForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    consent_text = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default="Active")

    def to_dict(self):
        return {
            'id': self.id,
            'patient_name': self.patient_name,
            'consent_text': self.consent_text,
            'language': self.language,
            'created_at': self.created_at,
            'expiry_date': self.expiry_date,
            'status': self.status
        }

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    token = create_access_token(identity=user.id)
    return jsonify({'token': token}), 200

@app.route('/consent_form', methods=['POST'])
@jwt_required()
def create_consent_form():
    data = request.get_json()
    new_form = ConsentForm(
        patient_name=data['patient_name'],
        consent_text=data['consent_text'],
        language=data['language'],
        expiry_date=datetime.utcnow() + timedelta(days=365)  # 1 year expiry
    )
    db.session.add(new_form)
    db.session.commit()
    return jsonify(new_form.to_dict()), 201

@app.route('/consent_forms', methods=['GET'])
@jwt_required()
def get_consent_forms():
    forms = ConsentForm.query.all()
    return jsonify([form.to_dict() for form in forms]), 200

@app.route('/consent_form/<int:form_id>', methods=['PUT'])
@jwt_required()
def update_consent_form(form_id):
    data = request.get_json()
    form = ConsentForm.query.get_or_404(form_id)
    form.status = data.get('status', form.status)
    form.expiry_date = data.get('expiry_date', form.expiry_date)
    db.session.commit()
    return jsonify(form.to_dict()), 200

def send_email(to, subject, body):
    from_email = "your_email@example.com"
    from_password = "your_password"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to

    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login(from_email, from_password)
        server.sendmail(from_email, to, msg.as_string())

def check_expiry():
    forms = ConsentForm.query.filter(ConsentForm.expiry_date <= datetime.utcnow() + timedelta(days=30)).all()
    for form in forms:
        send_email(to='admin@hospital.com', subject='Form Expiry Alert', body=f'Consent form for {form.patient_name} is expiring soon.')

from flask_cors import CORS
CORS(app)

if __name__ == '__main__':
    app.run(debug=True)