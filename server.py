from flask import Flask, request, Response,jsonify
import os
import subprocess
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import timedelta   
from dotenv import load_dotenv
app = Flask(__name__)

SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

app.config["JWT_SECRET_KEY"] = SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_BLACKLIST_ENABLED"] = True

jwt = JWTManager(app)

load_dotenv()

# In-memory token blacklist
blacklist = set()

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]  # Get the unique identifier for the token
    return jti in blacklist

os.environ["PATH"] += os.pathsep + r"C:\Users\raine\AppData\Local\MEGAcmd"

@app.route('/')
def home():
    return "Server is running!"

# Hardcoded credentials (for demonstration purposes)
USERS = {
    ADMIN_USERNAME: ADMIN_PASSWORD
}

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get("username")
    password = request.json.get("password")
    if USERS.get(username) == password:
        token = create_access_token(identity=username)
        return jsonify({"access_token": token}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/command', methods=['POST'])
@jwt_required()
def run_command():
    command = request.json.get('command')
    if command:
        try:
            # Use Popen to stream the command output in real-time
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            def generate():
                # Yield lines from the command's output
                for line in process.stdout:
                    yield line
                # Wait for the process to complete and yield any final errors
                process.wait()
                if process.returncode != 0:
                    yield f"Error: {process.stderr.read()}"
            
            return Response(generate(), mimetype='text/plain')
        except Exception as e:
            return {"error": str(e)}, 500
    else:
        return "No command received", 400
    
@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]  # Get the token's unique identifier
    blacklist.add(jti)      # Add the token to the blacklist
    return jsonify({"msg": "Successfully logged out"}), 200

@app.route('/restart', methods=['POST'])
@jwt_required
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
