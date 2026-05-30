from flask import Blueprint, request, jsonify
import jwt
from datetime import datetime, timedelta
import os

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # TODO: Hash password and store in database
    user = {
        'email': data['email'],
        'name': data.get('name', ''),
        'plan': 'free',
        'created_at': datetime.utcnow().isoformat()
    }
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user
    }), 201

@bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400
    
    # TODO: Validate credentials from database
    token = jwt.encode(
        {'email': data['email'], 'exp': datetime.utcnow() + timedelta(days=7)},
        SECRET_KEY,
        algorithm='HS256'
    )
    
    return jsonify({
        'message': 'Login successful',
        'token': token
    }), 200

@bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Verify JWT token"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return jsonify({'valid': True, 'email': payload['email']}), 200
    except jwt.InvalidTokenError:
        return jsonify({'valid': False, 'error': 'Invalid token'}), 401
