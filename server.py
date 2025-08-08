from flask import Flask, request, Response,jsonify, send_from_directory, render_template_string, flash, redirect, url_for
import os
import subprocess
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import timedelta   
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import logging 
from werkzeug.utils import secure_filename

app = Flask(__name__)

load_dotenv(dotenv_path=r'.env')

SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

app.config["JWT_SECRET_KEY"] = SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_BLACKLIST_ENABLED"] = True

jwt = JWTManager(app)

UPLOAD_FOLDER = r"E:\data"
ALLOWED_EXTENSIONS = {'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

blacklist = set()

USERS = {
    ADMIN_USERNAME: ADMIN_PASSWORD
}

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in blacklist

os.environ["PATH"] += os.pathsep + r"C:\Users\raine\AppData\Local\MEGAcmd"

# Configure logging to write to a file
logging.basicConfig(
    filename="flask_app.log",  # Log file name
    level=logging.DEBUG,  # Log all levels (INFO, DEBUG, ERROR)
    format="%(asctime)s [%(levelname)s] - %(message)s")  # Log format

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/datastore', methods=['POST'])
@jwt_required()
def upload_file():
    if 'file' not in request.files:
        return jsonify({"status": "No selected file"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"status": "uploaded", "filename": filename}), 200

    return jsonify({"status": "File type not allowed"}), 400


@app.route('/datastore/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_or_directory(path):
    full_path = os.path.join(app.static_folder, path)
    if os.path.isdir(full_path):
        files = os.listdir(full_path)
        return render_template_string(
            "<h1> Directory Listing for {{ path }}</h1>"
            "<ul>{% for file in files %}<li><a href='{{ path }}/{{ file }}'> {{ file }}</a></li>{% endfor %}</ul>",
            path=path, files=files
        )
    elif os.path.isfile(full_path):
        return send_from_directory(app.static_folder, path)
    else:
        return "File or directory not found", 404

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    print("Received Username:", username)
    print("Received Password:", password)
    print("Expected Username:", ADMIN_USERNAME)
    print("Expected Password:", ADMIN_PASSWORD)

    if USERS.get(username) == password:
        token = create_access_token(identity=username)
        return jsonify({"access_token": token}), 200
    return jsonify({"error": "Invalid credentials"}), 401

executor = ThreadPoolExecutor(max_workers=4)

@app.route('/command', methods=['POST'])
@jwt_required()
def run_command():
    logging.info(f"Received request: {request.json}")
    print(request.json)
    command = request.json.get('command')
    if not command:
        return jsonify({"error": "No command provided"}), 400

    future = executor.submit(subprocess.run, command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    result = future.result()  # Wait for command execution
    
    if result.returncode == 0:
        return jsonify({"success": True, "output": result.stdout.strip()})
    else:
        return jsonify({"success": False, "error": result.stderr.strip()}), 400
    
@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]  # Get the token's unique identifier
    blacklist.add(jti)      # Add the token to the blacklist
    return jsonify({"msg": "Successfully logged out"}), 200

@app.route('/restart', methods=['POST'])
@jwt_required()
def restart_task():
    process_name = request.json.get('process')
    start_command = request.json.get('start_command')

    if not process_name or not start_command:
        return jsonify({"error": "Process or start command missing"}), 400
    
    try:
        os.system(f"taskkill /IM {process_name} /F")
    except Exception as e:
        return jsonify({"error": f"Failed to kill process: {str(e)}"}), 500
    
    try:
        os.system(f'start "" "{start_command}"')
        return jsonify({"message": f"Successfully restarted {process_name}"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to restart process: {str(e)}"}), 500
    
@app.route('/debug', methods=['GET'])
def debug():
    return os.environ["PATH"]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
