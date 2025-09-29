
"""
Student Feedback Management System
Single-file prototype containing:
- Class blueprints (DatabaseConnection, Student, Admin, Feedback, Logger)
- Implementation of DatabaseConnection + exception handling
- Logger implementation (file-based)
- Flask app with routes for student register/login, submit_feedback,
  admin login and view_feedback, download logs

Notes:
- Uses mysql.connector (pip install mysql-connector-python)
- Uses Flask and Werkzeug for sessions and password hashing
- This is a starting point; in production you should use connection pooling,
  proper migrations, and stronger security.

To run:
1) Create a MySQL database `feedback_system` and create tables (example SQL below).
2) Update DB_CONFIG in this file with your DB credentials.
3) pip install -r requirements.txt (Flask, mysql-connector-python)
4) python student_feedback_system.py

Example DB schema (MySQL):

CREATE DATABASE feedback_system;
USE feedback_system;

CREATE TABLE students (
  student_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL
);

CREATE TABLE courses (
  course_id INT AUTO_INCREMENT PRIMARY KEY,
  course_name VARCHAR(255) NOT NULL,
  faculty_name VARCHAR(255) NOT NULL
);

CREATE TABLE feedback (
  feedback_id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  course_id INT NOT NULL,
  rating INT NOT NULL,
  comments TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY unique_feedback (student_id, course_id),
  FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
  FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
);

CREATE TABLE admins (
  admin_id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL
);

"""

from flask import Flask, render_template_string, request, redirect, url_for, session, send_file, abort
import mysql.connector
from mysql.connector import Error, IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import io

# ---------------------------
# Custom Exceptions
# ---------------------------
class DatabaseConnectionError(Exception):
    pass

class DuplicateFeedbackError(Exception):
    pass

class FileHandlingError(Exception):
    pass

class AuthenticationError(Exception):
    pass

# ---------------------------
# Logger class (file operations)
# ---------------------------
class Logger:
    def __init__(self, logfile='app.log'):
        self.logfile = logfile
        # ensure file exists
        try:
            open(self.logfile, 'a').close()
        except Exception as e:
            raise FileHandlingError(f"Cannot access log file {self.logfile}: {e}")

    def write_log(self, message: str):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            with open(self.logfile, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            raise FileHandlingError(f"Error writing to log file: {e}")

# ---------------------------
# DatabaseConnection class
# ---------------------------
class DatabaseConnection:
    def __init__(self, host='localhost', user='root', password='', database='feedback_system', logger: Logger = None):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self.cursor = None
        self.logger = logger or Logger()

    def connect(self):
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=False
            )
            self.cursor = self.conn.cursor(dictionary=True)
            self.logger.write_log('Database connected successfully.')
        except Error as e:
            # log and raise custom error
            try:
                self.logger.write_log(f'Database connection failed: {e}')
            except FileHandlingError:
                pass
            raise DatabaseConnectionError(str(e))

    def disconnect(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            self.logger.write_log('Database disconnected successfully.')
        except Exception as e:
            try:
                self.logger.write_log(f'Error during disconnect: {e}')
            except FileHandlingError:
                pass

    # convenience context manager
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc:
            # optionally rollback
            try:
                if self.conn:
                    self.conn.rollback()
            except Exception:
                pass
        else:
            try:
                if self.conn:
                    self.conn.commit()
            except Exception:
                pass
        self.disconnect()

# ---------------------------
# Data Models
# ---------------------------
class Feedback:
    def __init__(self, student_id: int, course_id: int, rating: int, comments: str = ''):
        self.student_id = student_id
        self.course_id = course_id
        self.rating = rating
        self.comments = comments
        self.created_at = datetime.now()

class Student:
    def __init__(self, dbconfig: dict, logger: Logger = None):
        self.dbconfig = dbconfig
        self.logger = logger or Logger()

    def register(self, name: str, email: str, password: str):
        hashed = generate_password_hash(password)
        try:
            with DatabaseConnection(logger=self.logger, **self.dbconfig) as db:
                sql = "INSERT INTO students (name, email, password) VALUES (%s, %s, %s)"
                db.cursor.execute(sql, (name, email, hashed))
                db.conn.commit()
                self.logger.write_log(f"Student registered: {email}")
                return True
        except IntegrityError as ie:
            # duplicate email
            self.logger.write_log(f"Duplicate registration attempt for {email}: {ie}")
            raise ie
        except DatabaseConnectionError as de:
            self.logger.write_log(f"DB connection error during registration for {email}: {de}")
            raise

    def login(self, email: str, password: str):
        try:
            with DatabaseConnection(logger=self.logger, **self.dbconfig) as db:
                sql = "SELECT * FROM students WHERE email = %s"
                db.cursor.execute(sql, (email,))
                row = db.cursor.fetchone()
                if row and check_password_hash(row['password'], password):
                    self.logger.write_log(f"Student login success: {email}")
                    return row  # return user row
                else:
                    self.logger.write_log(f"Student login failed: {email}")
                    raise AuthenticationError('Invalid credentials')
        except DatabaseConnectionError:
            raise

    def submit_feedback(self, feedback: Feedback):
        try:
            with DatabaseConnection(logger=self.logger, **self.dbconfig) as db:
                # check duplicate
                sql_check = "SELECT * FROM feedback WHERE student_id = %s AND course_id = %s"
                db.cursor.execute(sql_check, (feedback.student_id, feedback.course_id))
                if db.cursor.fetchone():
                    self.logger.write_log(f"Duplicate feedback attempt by student {feedback.student_id} for course {feedback.course_id}")
                    raise DuplicateFeedbackError('Feedback already submitted for this course by the student')

                sql_insert = "INSERT INTO feedback (student_id, course_id, rating, comments) VALUES (%s, %s, %s, %s)"
                db.cursor.execute(sql_insert, (feedback.student_id, feedback.course_id, feedback.rating, feedback.comments))
                db.conn.commit()
                self.logger.write_log(f"Feedback submitted by student {feedback.student_id} for course {feedback.course_id}")
                return True
        except DuplicateFeedbackError:
            raise
        except DatabaseConnectionError:
            raise
        except Exception as e:
            self.logger.write_log(f"Error during feedback submission: {e}")
            raise

class Admin:
    def __init__(self, dbconfig: dict, logger: Logger = None):
        self.dbconfig = dbconfig
        self.logger = logger or Logger()

    def login(self, username: str, password: str):
        try:
            with DatabaseConnection(logger=self.logger, **self.dbconfig) as db:
                sql = "SELECT * FROM admins WHERE username = %s"
                db.cursor.execute(sql, (username,))
                row = db.cursor.fetchone()
                if row and check_password_hash(row['password'], password):
                    self.logger.write_log(f"Admin login success: {username}")
                    return row
                else:
                    self.logger.write_log(f"Admin login failed: {username}")
                    raise AuthenticationError('Invalid admin credentials')
        except DatabaseConnectionError:
            raise

    def view_feedback(self):
        try:
            with DatabaseConnection(logger=self.logger, **self.dbconfig) as db:
                sql = ("SELECT f.feedback_id, f.student_id, s.name as student_name, f.course_id, c.course_name, c.faculty_name, f.rating, f.comments, f.created_at "
                       "FROM feedback f "
                       "JOIN students s ON f.student_id = s.student_id "
                       "JOIN courses c ON f.course_id = c.course_id "
                       "ORDER BY f.created_at DESC")
                db.cursor.execute(sql)
                rows = db.cursor.fetchall()
                self.logger.write_log('Admin viewed feedback list')
                return rows
        except DatabaseConnectionError:
            raise
        except Exception as e:
            self.logger.write_log(f"Error fetching feedback: {e}")
            raise

# ---------------------------
# Flask app wiring
# ---------------------------
app = Flask(__name__)
app.secret_key = os.environ.get('SFS_SECRET_KEY', 'dev-secret-key')

# configure DB credentials
DB_CONFIG = {
    'host': os.environ.get('SFS_DB_HOST', 'localhost'),
    'user': os.environ.get('SFS_DB_USER', 'root'),
    'password': os.environ.get('SFS_DB_PASS', ''),
    'database': os.environ.get('SFS_DB_NAME', 'feedback_system')
}

logger = Logger('app.log')
student_service = Student(dbconfig=DB_CONFIG, logger=logger)
admin_service = Admin(dbconfig=DB_CONFIG, logger=logger)

# Simple templates (for demo). In production, use separate HTML files.
REGISTER_TEMPLATE = """
<h2>Student Register</h2>
<form method="post">
  Name: <input name="name"><br>
  Email: <input name="email"><br>
  Password: <input type="password" name="password"><br>
  <button type="submit">Register</button>
</form>
<p>{{ message }}</p>
"""

LOGIN_TEMPLATE = """
<h2>Student Login</h2>
<form method="post">
  Email: <input name="email"><br>
  Password: <input type="password" name="password"><br>
  <button type="submit">Login</button>
</form>
<p>{{ message }}</p>
"""

SUBMIT_TEMPLATE = """
<h2>Submit Feedback</h2>
<p>Logged in as: {{ student_name }} (ID: {{ student_id }})</p>
<form method="post">
  Course: <select name="course_id">{% for c in courses %}<option value="{{ c.course_id }}">{{ c.course_name }} - {{ c.faculty_name }}</option>{% endfor %}</select><br>
  Rating (1-5): <input name="rating" type="number" min="1" max="5"><br>
  Comments: <br><textarea name="comments"></textarea><br>
  <button type="submit">Submit</button>
</form>
<p>{{ message }}</p>
"""

ADMIN_LOGIN_TEMPLATE = """
<h2>Admin Login</h2>
<form method="post">
  Username: <input name="username"><br>
  Password: <input type="password" name="password"><br>
  <button type="submit">Login</button>
</form>
<p>{{ message }}</p>
"""

ADMIN_VIEW_TEMPLATE = """
<h2>All Feedback</h2>
<p><a href="{{ url_for('download_logs') }}">Download Logs</a></p>
<table border="1" cellpadding="5" cellspacing="0">
  <tr><th>ID</th><th>Student</th><th>Course</th><th>Faculty</th><th>Rating</th><th>Comments</th><th>Created At</th></tr>
  {% for r in rows %}
  <tr>
    <td>{{ r.feedback_id }}</td>
    <td>{{ r.student_name }} ({{ r.student_id }})</td>
    <td>{{ r.course_name }}</td>
    <td>{{ r.faculty_name }}</td>
    <td>{{ r.rating }}</td>
    <td>{{ r.comments }}</td>
    <td>{{ r.created_at }}</td>
  </tr>
  {% endfor %}
</table>
"""

# Routes
@app.route('/')
def index():
    return "Student Feedback Management System - go to /register or /login"

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            student_service.register(name, email, password)
            message = 'Registered successfully. Please login.'
            return render_template_string(REGISTER_TEMPLATE, message=message)
        except IntegrityError:
            message = 'Email already registered.'
        except DatabaseConnectionError:
            message = 'Database connection error. Try later.'
        except Exception as e:
            message = f'Error: {e}'
    return render_template_string(REGISTER_TEMPLATE, message=message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = student_service.login(email, password)
            session['student_id'] = user['student_id']
            session['student_name'] = user['name']
            return redirect(url_for('submit_feedback'))
        except AuthenticationError:
            message = 'Invalid credentials.'
        except DatabaseConnectionError:
            message = 'Database connection error.'
        except Exception as e:
            message = f'Error: {e}'
    return render_template_string(LOGIN_TEMPLATE, message=message)

@app.route('/submit_feedback', methods=['GET', 'POST'])
def submit_feedback():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    message = ''
    student_id = session['student_id']
    student_name = session.get('student_name')
    # fetch courses
    try:
        with DatabaseConnection(logger=logger, **DB_CONFIG) as db:
            db.cursor.execute('SELECT * FROM courses')
            courses = db.cursor.fetchall()
    except DatabaseConnectionError:
        return 'DB connection error fetching courses', 500

    if request.method == 'POST':
        course_id = int(request.form.get('course_id'))
        rating = int(request.form.get('rating'))
        comments = request.form.get('comments')
        fb = Feedback(student_id=student_id, course_id=course_id, rating=rating, comments=comments)
        try:
            student_service.submit_feedback(fb)
            message = 'Feedback submitted successfully.'
        except DuplicateFeedbackError:
            message = 'You have already submitted feedback for this course.'
        except DatabaseConnectionError:
            message = 'DB connection error.'
        except Exception as e:
            message = f'Error: {e}'
    return render_template_string(SUBMIT_TEMPLATE, courses=courses, student_id=student_id, student_name=student_name, message=message)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            admin = admin_service.login(username, password)
            session['admin_id'] = admin['admin_id']
            session['admin_username'] = admin['username']
            return redirect(url_for('admin_view_feedback'))
        except AuthenticationError:
            message = 'Invalid admin credentials.'
        except DatabaseConnectionError:
            message = 'DB connection error.'
        except Exception as e:
            message = f'Error: {e}'
    return render_template_string(ADMIN_LOGIN_TEMPLATE, message=message)

@app.route('/admin/view_feedback')
def admin_view_feedback():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    try:
        rows = admin_service.view_feedback()
        return render_template_string(ADMIN_VIEW_TEMPLATE, rows=rows)
    except DatabaseConnectionError:
        return 'DB connection error.', 500
    except Exception as e:
        return f'Error: {e}', 500

@app.route('/admin/download_logs')
def download_logs():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    try:
        # serve the log file
        return send_file('app.log', as_attachment=True)
    except Exception as e:
        logger.write_log(f"Error serving log file: {e}")
        return 'Error serving log file', 500

# Run app
if __name__ == '__main__':
    # ensure log file exists
    try:
        logger.write_log('Application started')
    except FileHandlingError:
        print('Cannot access log file app.log')
    app.run(debug=True)
