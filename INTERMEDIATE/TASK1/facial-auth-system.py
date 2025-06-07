import cv2
import numpy as np
import os
import base64
from flask import Flask, render_template_string, Response, request, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "super_secret_key_for_sessions"
FACE_DIR = "registered_faces"
os.makedirs(FACE_DIR, exist_ok=True)

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
recognizer = cv2.face.LBPHFaceRecognizer_create()

CAMERA_SOUND_BASE64 = (
    "UklGRhIAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YYAAAP//AAD//wAA//8AAP//AAD//wAA//8AAP//"
    "AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8A"
    "AP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA"
)

APP_VERSION = "v1.1.0"
GITHUB_LINK = "https://github.com/manasa-09-tech/SlashMark/tree/main/INTERMEDIATE/TASK1"

BASE_STYLE = """
    <style>
        :root {
            --main-bg: #fffbe0;
            --main-accent: #ffe47a;
            --main-shadow: rgba(210, 180, 60, 0.10);
            --main-border: #ffe47a;
            --main-text: #243B55;
            --main-dark: #222;
            --success: #1b8146;
            --error: #d7263d;
            --footer: #b78906;
            --btn-hover: #ffb300;
        }
        [data-theme='dark'] {
            --main-bg: #191c24;
            --main-accent: #23272f;
            --main-shadow: rgba(0,0,0,0.8);
            --main-border: #ffe47a;
            --main-text: #ffe47a;
            --main-dark: #fff;
            --success: #43e97b;
            --error: #ff6877;
            --footer: #ffe47a;
            --btn-hover: #ffe47a;
        }
        body {
            background: linear-gradient(135deg, var(--main-bg), var(--main-accent) 70%);
            font-family: 'Segoe UI', Arial, sans-serif;
            color: var(--main-text);
            margin: 0;
            min-height: 100vh;
            transition: background 0.2s,color 0.2s;
        }
        header {
            background: linear-gradient(90deg, var(--main-accent), var(--main-bg) 85%);
            color: #3a2c00;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            position: relative;
        }
        [data-theme='dark'] header {
            background: linear-gradient(90deg, #23272f, #191c24 85%);
            color: #ffe47a;
        }
        .theme-toggle {
            position: absolute;
            right: 2.3rem;
            top: 2.4rem;
            font-size: 1.1rem;
            padding: 4px 10px;
            border-radius: 6px;
            background: var(--main-accent);
            color: #3a2c00;
            border: none;
            box-shadow: 0 2px 8px var(--main-shadow);
            cursor: pointer;
        }
        [data-theme='dark'] .theme-toggle {
            background: #ffe47a;
            color: #23272f;
        }
        .theme-toggle:hover {
            background: var(--btn-hover);
        }
        main {
            max-width: 480px;
            background: white;
            margin: 2rem auto 0 auto;
            border-radius: 18px;
            box-shadow: 0 8px 36px 0 var(--main-shadow);
            padding: 2rem 2.5rem 2rem 2.5rem;
            position: relative;
        }
        [data-theme='dark'] main {
            background: #23272f !important;
            color: #ffe47a !important;
        }
        h1, h2 {
            font-weight: 700;
            margin-top: 0;
            letter-spacing: 1px;
        }
        [data-theme='dark'] h1, [data-theme='dark'] h2 {
            color: #ffe47a !important;
        }
        ul {
            list-style: none;
            padding: 0;
            text-align: center;
        }
        ul li {
            display: inline-block;
            margin: 0 1.2rem;
        }
        a {
            color: var(--footer);
            text-decoration: none;
            font-weight: bold;
            transition: color 0.2s;
        }
        a:hover {
            color: var(--btn-hover);
        }
        [data-theme='dark'] a {
            color: #ffe47a !important;
        }
        form {
            margin-bottom: 1.2rem;
            text-align: center;
        }
        input[type="text"] {
            padding: 0.5rem;
            border-radius: 8px;
            border: 1px solid var(--main-border);
            font-size: 1rem;
            margin-bottom: 1rem;
            width: 70%;
            outline: none;
            transition: border 0.2s;
        }
        input[type="text"]:focus {
            border: 1.5px solid var(--main-border);
        }
        [data-theme='dark'] input[type="text"] {
            background: #23272f;
            color: #ffe47a;
            border: 1.5px solid #ffe47a;
        }
        button {
            background: linear-gradient(90deg, var(--main-accent) 50%, var(--main-bg) 100%);
            color: #3a2c00;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 1.6rem;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 2px 8px var(--main-shadow);
            transition: background 0.2s;
        }
        button:active {
            background: var(--main-accent);
        }
        button:hover {
            background: var(--btn-hover);
        }
        [data-theme='dark'] button {
            background: #ffe47a !important;
            color: #23272f !important;
        }
        .note, .about-section, .security-warning, .device-tip {
            font-size: 1rem;
            margin: 1.5rem 0 1rem 0;
            color: #856000;
            background: #fffbe0;
            padding: 1rem;
            border-radius: 10px;
            border-left: 5px solid var(--main-border);
        }
        [data-theme='dark'] .note, 
        [data-theme='dark'] .about-section, 
        [data-theme='dark'] .security-warning, 
        [data-theme='dark'] .device-tip {
            background: #23272f !important;
            color: #ffe47a !important;
            border-color: #ffe47a !important;
        }
        .success {
            color: var(--success);
            font-weight: 600;
        }
        .error {
            color: var(--error);
            font-weight: 600;
        }
        .footer {
            text-align: center;
            margin: 2.5rem 0 1rem 0;
            font-size: 1rem;
            color: var(--footer);
        }
        .footer-links {
            margin-top: 0.3rem;
            font-size: 0.92rem;
        }
        .footer-links a {
            color: var(--footer);
            margin: 0 0.7rem;
        }
        [data-theme='dark'] .footer, 
        [data-theme='dark'] .footer-links a {
            color: #ffe47a !important;
        }
        .version-badge {
            display: inline-block;
            margin-left: 0.6rem;
            padding: 3px 9px;
            font-size: 0.9rem;
            border-radius: 7px;
            background: var(--main-accent);
            color: #3a2c00;
            font-weight: bold;
        }
        [data-theme='dark'] .version-badge {
            background: #23272f;
            color: #ffe47a;
            border: 1px solid #ffe47a;
        }
        .users-count {
            text-align: center;
            margin: 0.7rem 0 0.8rem 0;
            font-size: 1.13rem;
        }
        .users-count span {
            background: #fffbe0;
            color: var(--footer);
            border-radius: 8px;
            padding: 4px 19px;
            margin: 0 6px;
            font-weight: 600;
            font-size: 1.17rem;
            box-shadow: 0 1px 4px var(--main-shadow);
            display: inline-block;
        }
        [data-theme='dark'] .users-count span {
            background: #23272f;
            color: #ffe47a;
        }
        .activity {
            text-align: center;
            color: #3a2c00;
            font-size: 1.01rem;
            margin-top: 0.7rem;
        }
        [data-theme='dark'] .activity {
            color: #ffe47a;
        }
        .sidebyside {
            display: flex;
            justify-content: center;
            align-items: flex-start;
            gap: 28px;
        }
        .sidebyside img {
            width: 160px;
            height: 160px;
            margin: 0;
            border: 2.5px solid var(--main-border);
            box-shadow: 0 2px 8px var(--main-shadow);
        }
        .caption {
            text-align: center;
            font-size: 1rem;
            font-weight: 500;
            margin-top: 0.4rem;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 999;
            left: 0;
            top: 0;
            width: 100vw;
            height: 100vh;
            overflow: auto;
            background: rgba(0,0,0,0.32);
        }
        .modal-content {
            background: #fffbe0;
            margin: 8% auto;
            padding: 2.3rem 2rem 2rem 2rem;
            border: 2px solid #ffe47a;
            border-radius: 12px;
            width: 98%;
            max-width: 410px;
            box-shadow: 0 8px 36px 0 var(--main-shadow);
            color: #222;
            position: relative;
        }
        [data-theme='dark'] .modal-content {
            background: #23272f !important;
            color: #ffe47a !important;
            border-color: #ffe47a !important;
        }
        .close {
            color: #aaa;
            position: absolute;
            right: 1.1rem;
            top: 1.1rem;
            font-size: 2rem;
            font-weight: bold;
            cursor: pointer;
        }
        [data-theme='dark'] .close {
            color: #ffe47a;
        }
        .modal-content h2 {
            margin-top: 0;
            color: #b78906;
        }
        [data-theme='dark'] .modal-content h2 {
            color: #ffe47a;
        }
        @media (max-width: 600px) {
            main {
                padding: 1.2rem 0.8rem;
                max-width: 98%;
            }
            .theme-toggle {
                right: 1.2rem;
                top: 1.1rem;
                font-size: 1rem;
            }
        }
    </style>
"""

THEME_SCRIPT = """
    <script>
        function toggleTheme() {
            let current = document.body.getAttribute('data-theme');
            if (!current || current === 'light') {
                document.body.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
            } else {
                document.body.setAttribute('data-theme', 'light');
                localStorage.setItem('theme', 'light');
            }
        }
        (function() {
            let theme = localStorage.getItem('theme');
            if (theme) document.body.setAttribute('data-theme', theme);
        })();
        function showModal(id) {
            document.getElementById(id).style.display = 'block';
        }
        function closeModal(id) {
            document.getElementById(id).style.display = 'none';
        }
        window.onclick = function(event) {
            let modal = document.getElementById('helpModal');
            if (modal && event.target === modal) modal.style.display = "none";
        }
    </script>
"""

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Facial Authentication System</title>
    {{ BASE_STYLE|safe }}
</head>
<body>
    <header>
        <button class="theme-toggle" onclick="toggleTheme()" title="Toggle theme">&#9788;</button>
        <h1>Web-Based Facial Authentication System</h1>
    </header>
    <main>
        <ul>
            <li><a href="{{ url_for('register') }}">Register Face</a></li>
            <li><a href="{{ url_for('login') }}">Authenticate (Login)</a></li>
            <li><a href="#" onclick="showModal('helpModal'); return false;">How it Works?</a></li>
        </ul>
        <div class="users-count">
            <b>Registered Users:</b>
            <span>{{ users_count }}</span>
        </div>
        {% if last_login %}
        <div class="activity">
            <span>Last login: <b>{{ last_login }}</b></span>
        </div>
        {% endif %}
        <div class="about-section">
            <b>About:</b> This demo provides real-time, web-based facial authentication using Python, OpenCV, and Flask.
        </div>
        <div class="note">
            <b>Extensible for:</b> meetings, exams, police force, phone unlock, and more.<br>
            <b>No external dependencies beyond OpenCV and Flask.</b>
        </div>
        <div class="security-warning">
            <b>Security:</b> This is a prototype for demonstration purposes, not for production use.
        </div>
        <div class="device-tip">
            <b>Tip:</b> For best results, use a desktop/laptop with a webcam. Mobile browsers may not support webcam access.
        </div>
    </main>
    <div class="footer">
        DY MANASA
        <span class="version-badge">{{ version }}</span>
        <div class="footer-links">
            <a href="{{ github_link }}" target="_blank">GitHub</a>
        </div>
    </div>
    <div id="helpModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('helpModal')">&times;</span>
            <h2>How it Works?</h2>
            <ol style="margin-left:0;">
                <li><b>Register Face:</b> Click "Register Face", enter a username, and let the system capture your face from the webcam.</li>
                <li><b>Authenticate (Login):</b> Click "Authenticate (Login)" and the app will try to match your face.</li>
                <li><b>Result:</b> If matched, your username will be shown. For best results, use similar lighting and face position as during registration.</li>
            </ol>
            <ul style="margin-top:1.1rem;">
                <li>Ensure only one face is visible during registration/login.</li>
                <li>You can register multiple users, each with a unique username.</li>
                <li>If you encounter issues, make sure your webcam is accessible.</li>
            </ul>
        </div>
    </div>
    {{ THEME_SCRIPT|safe }}
</body>
</html>
"""

REGISTER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Register Face</title>
    {{ BASE_STYLE|safe }}
</head>
<body>
    <header>
        <button class="theme-toggle" onclick="toggleTheme()" title="Toggle theme">&#9788;</button>
        <h2>Register Your Face</h2>
    </header>
    <main>
        <form method="POST" id="registerForm">
            <input type="text" name="username" placeholder="Enter username" required><br>
            <button type="submit" id="captureBtn">Capture and Register Face</button>
        </form>
        <audio id="camera-audio" preload="auto">
            <source src="data:audio/wav;base64,{{ CAMERA_SOUND_BASE64 }}" type="audio/wav">
        </audio>
        <script>
        function playCameraSoundAndDelaySubmit(e) {
            var audio = document.getElementById('camera-audio');
            if (audio) {
                e.preventDefault();
                audio.currentTime = 0;
                audio.play();
                setTimeout(function() {
                    document.getElementById("registerForm").submit();
                }, 400);
            }
        }
        document.getElementById('registerForm').addEventListener('submit', playCameraSoundAndDelaySubmit);
        document.getElementById('captureBtn').addEventListener('click', function(e){
            var audio = document.getElementById('camera-audio');
            if(audio) { audio.currentTime = 0; audio.play(); }
        });
        </script>
        <p><a href="{{ url_for('index') }}">&larr; Back to Home</a></p>
        <img src="{{ url_for('video_feed', mode='register') }}" width="320" height="240">
        {% if capture_status %}
        <p class="{{ 'success' if capture_status == 'success' else 'error' }}">
            {{ capture_message }}
        </p>
        {% endif %}
        {% if message %}
        <p class="{{ 'success' if 'registered' in message else 'error' }}">{{ message }}</p>
        {% endif %}
    </main>
    <div class="footer">
        DY MANASA <span class="version-badge">{{ version }}</span>
        <div class="footer-links">
            <a href="{{ github_link }}" target="_blank">GitHub</a>
        </div>
    </div>
    {{ THEME_SCRIPT|safe }}
</body>
</html>
"""

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Face Login</title>
    {{ BASE_STYLE|safe }}
</head>
<body>
    <header>
        <button class="theme-toggle" onclick="toggleTheme()" title="Toggle theme">&#9788;</button>
        <h2>Face Authentication (Login)</h2>
    </header>
    <main>
        <form method="POST">
            <button type="submit">Authenticate with Webcam</button>
        </form>
        <img src="{{ url_for('video_feed', mode='login') }}" width="320" height="240">
        {% if registered_img_b64 and current_img_b64 %}
        <div class="sidebyside" style="margin-top:1.2rem;">
            <div>
                <img src="data:image/png;base64,{{ registered_img_b64 }}">
                <div class="caption">Registered</div>
            </div>
            <div>
                <img src="data:image/png;base64,{{ current_img_b64 }}">
                <div class="caption">Now</div>
            </div>
        </div>
        {% endif %}
        {% if confidence is not none %}
        <div style="text-align:center; margin-top:0.8rem;">
            <b>Match Confidence:</b> {{ confidence|round(2) }}
        </div>
        {% endif %}
        {% if message %}
        <p class="{{ 'success' if 'Authenticated' in message else 'error' }}">{{ message }}</p>
        {% endif %}
        <p><a href="{{ url_for('index') }}">&larr; Back to Home</a></p>
    </main>
    <div class="footer">
        DY MANASA <span class="version-badge">{{ version }}</span>
        <div class="footer-links">
            <a href="{{ github_link }}" target="_blank">GitHub</a>
        </div>
    </div>
    {{ THEME_SCRIPT|safe }}
</body>
</html>
"""

def get_registered_users():
    return [f.split(".")[0] for f in os.listdir(FACE_DIR) if f.endswith(".png")]

def train_recognizer():
    images, labels = [], []
    for user in get_registered_users():
        img_path = os.path.join(FACE_DIR, f"{user}.png")
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is not None:
            images.append(img)
            labels.append(user)
    if images:
        label_ids = {name: idx for idx, name in enumerate(labels)}
        rev_labels = {v: k for k, v in label_ids.items()}
        recognizer.train(images, np.array([label_ids[l] for l in labels]))
        return label_ids, rev_labels
    else:
        return {}, {}

@app.route('/')
def index():
    users_count = len(get_registered_users())
    last_login = session.get("last_login")
    return render_template_string(
        INDEX_HTML,
        BASE_STYLE=BASE_STYLE,
        THEME_SCRIPT=THEME_SCRIPT,
        users_count=users_count,
        last_login=last_login,
        version=APP_VERSION,
        github_link=GITHUB_LINK
    )

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ""
    capture_status = ""
    capture_message = ""
    if request.method == "POST":
        username = request.form['username']
        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()
        cam.release()
        if not ret:
            capture_status = "fail"
            capture_message = "Webcam error: Could not capture image."
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            if len(faces) != 1:
                capture_status = "fail"
                if len(faces) == 0:
                    capture_message = "No face detected. Please try again."
                else:
                    capture_message = "Multiple faces detected. Please ensure only your face is visible."
            else:
                (x, y, w, h) = faces[0]
                face_img = gray[y:y+h, x:x+w]
                face_img = cv2.resize(face_img, (200, 200))
                cv2.imwrite(os.path.join(FACE_DIR, f"{username}.png"), face_img)
                capture_status = "success"
                capture_message = "Picture captured and saved successfully."
                message = f"Face registered for {username}."
    return render_template_string(
        REGISTER_HTML,
        message=message,
        BASE_STYLE=BASE_STYLE,
        THEME_SCRIPT=THEME_SCRIPT,
        capture_status=capture_status,
        capture_message=capture_message,
        CAMERA_SOUND_BASE64=CAMERA_SOUND_BASE64,
        version=APP_VERSION,
        github_link=GITHUB_LINK
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ""
    confidence = None
    registered_img_b64 = None
    current_img_b64 = None
    user = None
    if request.method == "POST":
        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()
        cam.release()
        if not ret:
            message = "Webcam error."
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            if len(faces) != 1:
                message = "Please ensure exactly one face is visible."
            else:
                (x, y, w, h) = faces[0]
                face_img = gray[y:y+h, x:x+w]
                face_img = cv2.resize(face_img, (200, 200))
                label_ids, rev_labels = train_recognizer()
                if not label_ids:
                    message = "No faces registered yet."
                else:
                    pred_label, confidence_val = recognizer.predict(face_img)
                    confidence = confidence_val
                    user = rev_labels.get(pred_label)
                    registered_img_path = os.path.join(FACE_DIR, f"{user}.png") if user else None
                    if registered_img_path and os.path.exists(registered_img_path):
                        with open(registered_img_path, "rb") as f:
                            registered_img_b64 = base64.b64encode(f.read()).decode("utf-8")
                    _, curr_buf = cv2.imencode(".png", face_img)
                    current_img_b64 = base64.b64encode(curr_buf).decode("utf-8")
                    if user and confidence < 70:
                        message = f"Authenticated as {user} (confidence: {confidence:.2f})"
                        session["last_login"] = datetime.now().strftime("%Y-%m-%d %I:%M %p")
                    elif user:
                        message = f"Face detected as {user}, but authentication failed (confidence: {confidence:.2f})."
                    else:
                        message = "Authentication failed."
    return render_template_string(
        LOGIN_HTML,
        message=message,
        BASE_STYLE=BASE_STYLE,
        THEME_SCRIPT=THEME_SCRIPT,
        registered_img_b64=registered_img_b64,
        current_img_b64=current_img_b64,
        confidence=confidence,
        version=APP_VERSION,
        github_link=GITHUB_LINK
    )

@app.route('/video_feed')
def video_feed():
    mode = request.args.get('mode')
    def stream():
        cam = cv2.VideoCapture(0)
        height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        scan_pos = 0
        direction = 1  # 1: down, -1: up
        while True:
            ret, frame = cam.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 193, 7), 2)
            # --- SCANNING LINE EFFECT ---
            scan_thickness = 3
            scan_color = (0, 255, 0)  # Bright green
            scan_pos += direction * 6  # speed
            if scan_pos >= height - 1:
                scan_pos = height - 1
                direction = -1
            elif scan_pos <= 0:
                scan_pos = 0
                direction = 1
            cv2.line(frame, (0, scan_pos), (frame.shape[1], scan_pos), scan_color, scan_thickness)
            ret2, buffer = cv2.imencode('.jpg', frame)
            if not ret2:
                continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        cam.release()
    return Response(stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    try:
        _ = cv2.face.LBPHFaceRecognizer_create
    except AttributeError:
        print("Please install opencv-contrib-python: pip install opencv-contrib-python")
        exit(1)
    app.run(host='0.0.0.0', port=5000, debug=True)