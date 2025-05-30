# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
from werkzeug.utils import secure_filename
import requests

app = Flask(__name__)
app.secret_key = "your_secret_key"

DB_PATH = "NumberPlate.db"
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# --- Utility Functions ---

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)  # add timeout
    conn.row_factory = sqlite3.Row
    return conn


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_number_plate(image_path):
    API_URL = "https://api-inference.huggingface.co/models/your-model-name"
    headers = {"Authorization": "Bearer YOUR_HUGGINGFACE_API_TOKEN"}

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    response = requests.post(API_URL, headers=headers, data=image_bytes)

    if response.status_code == 200:
        result = response.json()
        if isinstance(result, list) and len(result) > 0 and 'label' in result[0]:
            return result[0]['label'].strip().upper()
        elif isinstance(result, dict) and 'text' in result:
            return result['text'].strip().upper()
        else:
            return None
    else:
        print("Error:", response.status_code, response.text)
        return None

# --- Routes ---

@app.route('/huggingface')
def embed_hf():
    return render_template('huggingface.html')


@app.route('/')
def index():
    return render_template('index.html')
  
@app.route('/detections')
def view_detections():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    records = conn.execute('SELECT * FROM detections ORDER BY timestamp DESC').fetchall()
    conn.close()
    return render_template('detections.html', records=records)

# @app.route('/detection_stats')
# def detection_stats():
#     if not session.get('admin_logged_in'):
#         return redirect(url_for('login'))
#     conn = get_db_connection()
#     stats = conn.execute('''
#         SELECT car_number, DATE(timestamp) as date, COUNT(*) as count
#         FROM detections
#         GROUP BY car_number, DATE(timestamp)
#         ORDER BY date DESC, car_number
#     ''').fetchall()
#     conn.close()
#     return render_template('detection_stats.html', stats=stats)

@app.route('/detection_stats')
def detection_stats():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    stats = conn.execute('''
        SELECT name, car_number, DATE(timestamp) as date, COUNT(*) as count
        FROM detections
        GROUP BY name, car_number, DATE(timestamp)
        ORDER BY date DESC, count DESC
    ''').fetchall()
    conn.close()

    return render_template('detection_stats.html', stats=stats)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        car_number = request.form['car_number'].upper().strip()
        email = request.form['email']
        flat_number = request.form['flat_number']

        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO users (name, mobile, car_number, email, flat_number) VALUES (?, ?, ?, ?, ?)',
                (name, mobile, car_number, email, flat_number)
            )
            conn.commit()
            flash("Registration successful!", "success")
        except sqlite3.IntegrityError:
            flash("Car number already registered!", "danger")
        finally:
            conn.close()

        return render_template('index.html')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid username or password", "danger")

    return render_template('login.html')
  


@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()

    return render_template('admin_dashboard.html', users=users)

@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    message = None
    if request.method == 'POST':
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            detected_plate = "EXAMPLE1234"  # Replace with real detection logic or integrate Hugging Face API
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            conn = get_db_connection()
            conn.execute("INSERT INTO detections (car_number, timestamp) VALUES (?, ?)", (detected_plate, timestamp))
            user = conn.execute("SELECT * FROM users WHERE car_number = ?", (detected_plate,)).fetchone()
            conn.commit()
            conn.close()

            if user:
              message = u"✅Plate matched: {}".format(user['name'])
            else:
              message = u"❌ Plate {} not found.".format(detected_plate)

        else:
            message = "Invalid or no file uploaded."
    return render_template('upload.html', message=message)
  
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))

# --- New API Endpoint to Verify Plate and Return User Details ---
# @app.route('/verify_plate', methods=['POST'])
# def verify_plate():
#     plate_number = request.form.get('car_number')
#     if not plate_number:
#         return jsonify({"status": "error", "message": "No license number provided"}), 400

#     conn = get_db_connection()
#     cursor = conn.cursor()

#     # Log detection
#     conn.execute(
#         "INSERT INTO detections (car_number) VALUES (?)",
#         (plate_number.strip().upper(),)
#     )
#     conn.commit()

#     cursor.execute(
#         "SELECT name, mobile, flat_number, email FROM users WHERE car_number = ?",
#         (plate_number.strip().upper(),)
#     )
#     result = cursor.fetchone()
#     conn.close()

#     if result:
#         name, mobile, flat_number, email = result
#         return jsonify({
#             "status": "success",
#             "message": "Match found",
#             "data": {
#                 "name": name,
#                 "mobile": mobile,
#                 "flat_number": flat_number,
#                 "email": email,
#                 "car_number": plate_number.strip().upper()
#             }
#         }), 200
#     else:
#         return jsonify({"status": "fail", "message": "No match found"}), 404
   
@app.route('/verify_plate', methods=['POST'])
def verify_plate():
    plate_number = request.form.get('car_number')
    if not plate_number:
        return jsonify({"status": "error", "message": "No license number provided"}), 400

    car_number = plate_number.strip().upper()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Try to find the user
    cursor.execute("SELECT name, mobile, flat_number, email FROM users WHERE car_number = ?", (car_number,))
    result = cursor.fetchone()

    # Record detection (with name or Unknown)
    name_to_store = result[0] if result else "Unknown"
    conn.execute("INSERT INTO detections (car_number, name) VALUES (?, ?)", (car_number, name_to_store))
    conn.commit()

    conn.close()

    if result:
        name, mobile, flat_number, email = result
        return jsonify({
            "status": "success",
            "message": "Match found",
            "data": {
                "name": name,
                "mobile": mobile,
                "flat_number": flat_number,
                "email": email,
                "car_number": car_number
            }
        }), 200
    else:
        return jsonify({"status": "fail", "message": "No match found"}), 404

      
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)