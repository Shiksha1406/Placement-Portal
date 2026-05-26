import jwt
import datetime
from flask import jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models import User, Student, Company


def register(req):
    data = req.json
    if not data:
        return jsonify({'message': 'Invalid or missing JSON body'}), 400

    role = data['role'].lower()
    if role == 'admin':
         return jsonify({
            'message': 'Admin registration is not allowed. '
                       'Please contact the system administrator.'
        }), 403

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400

    hashed_pw = generate_password_hash(data['password'], method='pbkdf2:sha256')
    user = User(
        username=data['username'],
        password=hashed_pw,
        role=role
    )
    db.session.add(user)
    db.session.flush()  


    # Create role-specific record
    if role == 'student':
        student = Student(user_id=user.id, department='', name=data.get('name', ''))
        db.session.add(student)
    elif role == 'company':
        company = Company(user_id=user.id, approved=False)
        db.session.add(company)

    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201


def login(req):
    data = req.json
    if not data:
        return jsonify({'message': 'Invalid or missing JSON body'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid username or password'}), 401
    
    if user.is_blacklisted:
        return jsonify({'message': 'Your account has been blacklisted'}), 403

    token = jwt.encode({
        'user_id': user.id,
        'role': user.role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')


    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'role': user.role
        }
    }), 200
