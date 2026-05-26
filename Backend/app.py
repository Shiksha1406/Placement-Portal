from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask,jsonify
from flask_cors import CORS
from extensions import cache, limiter, mail
from database import db
from routes.auth_routes import auth_bp
from routes.student_routes import student_bp
from routes.company_routes import company_bp
from routes.admin_routes import admin_bp
from models import User
from werkzeug.security import generate_password_hash


app = Flask(__name__)
app.config.from_object('config.Config')

CORS(app)
db.init_app(app)
mail.init_app(app)
cache.init_app(app)   
limiter.init_app(app)

    
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'message': 'Too many requests. Please slow down.',
        'retry_after': str(e.description)
    }), 429  


with app.app_context():
    db.create_all()
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


    if not User.query.filter_by(role='admin').first():
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin@123')
        admin_user = User(
            username=admin_username,
            password=generate_password_hash(admin_password, method='pbkdf2:sha256'),
            role='admin',
        )
        db.session.add(admin_user)
        db.session.commit()
        print(f'[app] Admin account seeded — username: {admin_username}')

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(student_bp, url_prefix='/students')
app.register_blueprint(company_bp, url_prefix='/companies')
app.register_blueprint(admin_bp, url_prefix='/admin')


if __name__ == '__main__':
     app.run(debug=True)
       
