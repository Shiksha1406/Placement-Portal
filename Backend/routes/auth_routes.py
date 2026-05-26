from flask import Blueprint, request
from controllers.auth_controller import register, login 
from extensions import limiter 

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])   #Used to create a new user 
def register_route():
    return register(request)


@auth_bp.route('/login', methods=['POST'])  
@limiter.limit("10 per minute;50 per hour")   
def login_route():
    return login(request)

# @auth_bp.route('/login', methods=['GET'])
# def test_login():
#     return "Login route working"
