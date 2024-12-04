from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
from marshmallow import Schema, fields, ValidationError
import logging
import traceback

# --- Flask App Setup ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin123@db:5432/courses_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # Para depurar SQL
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
limiter = Limiter(key_func=get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])

# --- Logger Setup ---
logging.basicConfig(filename="api.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def log_request(action, details):
    logging.info(f"{action}: {details}")

# --- Models ---
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    instructor = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    enrollment_limit = db.Column(db.Integer)

# --- Validation Schema ---
class CourseSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str()
    instructor = fields.Str(required=True)
    duration = fields.Int(required=True)
    enrollment_limit = fields.Int()

course_schema = CourseSchema()

# --- Error Handling ---
@app.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify({"error": error.messages}), 400

@app.errorhandler(404)
def handle_not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(403)
def handle_forbidden_error(error):
    return jsonify({"error": "Forbidden"}), 403

@app.errorhandler(500)
def handle_internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/courses')
def courses_page():
    return render_template('courses.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        username = request.json.get('username')
        password = request.json.get('password')
        role = request.json.get('role', 'user')

        if not username or not password:
            return jsonify({"msg": "Username and password are required"}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"msg": "Username already exists"}), 400

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password_hash=password_hash, role=role)

        db.session.add(new_user)
        db.session.commit()

        log_request("User Registration", f"User '{username}' registered with role '{role}'")
        return jsonify({"msg": f"User '{username}' created successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({"msg": "Error registering user", "error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.json.get('username')
        password = request.json.get('password')

        user = User.query.filter_by(username=username).first()
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            return jsonify({"msg": "Bad username or password"}), 401

        access_token = create_access_token(identity={"username": user.username, "role": user.role})
        log_request("User Login", f"User '{username}' logged in")
        return jsonify(access_token=access_token, role=user.role)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"msg": "Error logging in", "error": str(e)}), 500

@app.route('/courses', methods=['POST'])
@jwt_required()
def create_course():
    try:
        current_user = get_jwt_identity()
        if current_user['role'] not in ['admin', 'editor']:
            return jsonify({"msg": "Permission denied. Only Admins and Editors can create courses."}), 403

        data = course_schema.load(request.json)
        new_course = Course(**data)
        db.session.add(new_course)
        db.session.commit()

        log_request("Course Created", f"Course '{data['title']}' created by {current_user['username']}")
        return jsonify({"msg": "Course created successfully!"}), 201
    except ValidationError as ve:
        logging.error(f"Validation error: {ve.messages}")
        return jsonify({"msg": "Invalid course data", "errors": ve.messages}), 400
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({"msg": "Error creating course", "error": str(e)}), 500

@app.route('/courses', methods=['GET'])
@jwt_required()
def get_courses():
    try:
        courses = Course.query.all()  # Consulta la base de datos
        if not courses:
            return jsonify({"msg": "No courses available"}), 404

        return jsonify([{
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "instructor": course.instructor,
            "duration": course.duration,
            "enrollment_limit": course.enrollment_limit
        } for course in courses]), 200

    except Exception as e:
        # Registro del error en el log
        logging.error(f"Error fetching courses: {e}")
        traceback.print_exc()
        return jsonify({"msg": "Error fetching courses", "error": str(e)}), 500

@app.route('/health/liveness', methods=['GET'])
def liveness():
    return jsonify({"status": "alive"}), 200

@app.route('/health/readiness', methods=['GET'])
def readiness():
    try:
        db.session.execute('SELECT 1')
        return jsonify({"status": "ready"}), 200
    except Exception:
        return jsonify({"status": "not ready"}), 500


# --- Initialize Database ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000 , debug=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True)

