import os
import json
from flask import Flask, request, render_template_string, redirect, url_for, flash
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

# --- Configuration & Setup ---
ENCRYPTION_KEY_BASE64 = os.environ.get("ENCRYPTION_KEY_BASE64")
if ENCRYPTION_KEY_BASE64:
    KEY = base64.b64decode(ENCRYPTION_KEY_BASE64)
else:
    KEY = get_random_bytes(32)
    print("Generated new AES key (base64):", base64.b64encode(KEY).decode())

ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "manasa")
DATA_FILE = "cards.json"

# --- Cryptography Functions ---
def encrypt_card(card_number: str) -> str:
    cipher = AES.new(KEY, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(card_number.encode())
    encrypted_data = base64.b64encode(cipher.nonce + tag + ciphertext).decode()
    return encrypted_data

def decrypt_card(encrypted_data: str) -> str:
    bdata = base64.b64decode(encrypted_data)
    nonce, tag, ciphertext = bdata[:16], bdata[16:32], bdata[32:]
    cipher = AES.new(KEY, AES.MODE_GCM, nonce=nonce)
    card_number = cipher.decrypt_and_verify(ciphertext, tag)
    return card_number.decode()

def store_to_local(card_id: str, encrypted_data: str):
    try:
        cards = {}
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                cards = json.load(f)
        cards[card_id] = encrypted_data
        with open(DATA_FILE, "w") as f:
            json.dump(cards, f)
    except Exception as e:
        raise RuntimeError(f"Local storage error: {e}")

def retrieve_from_local(card_id: str) -> str:
    try:
        if not os.path.exists(DATA_FILE):
            raise KeyError("Card not found.")
        with open(DATA_FILE, "r") as f:
            cards = json.load(f)
        return cards[card_id]
    except KeyError:
        raise KeyError("Card not found.")
    except Exception as e:
        raise RuntimeError(f"Local retrieval error: {e}")

# --- Flask App and Routes ---
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersecretflaskkey")

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <title>Secure Credit Card Vault</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500&family=Roboto:wght@400;700&display=swap');
    body {
        background: linear-gradient(135deg, #4e54c8, #8f94fb);
        font-family: 'Montserrat', 'Roboto', Arial, sans-serif;
        color: #222;
        margin: 0;
        padding: 0;
        min-height: 100vh;
    }
    .container {
        max-width: 430px;
        margin: 48px auto;
        background: #fff;
        border-radius: 22px;
        box-shadow: 0 8px 40px 4px rgba(78,84,200,0.12);
        padding: 2.2rem 2.7rem 2.5rem 2.7rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .header-img {
        width: 85px;
        margin-bottom: 1em;
        margin-top: -1.5em;
        animation: float 2.5s infinite alternate ease-in-out;
    }
    @keyframes float {
        to { transform: translateY(-10px); }
    }
    h1 {
        font-size: 2.15em;
        margin-bottom: 0.2em;
        color: #4e54c8;
        font-family: 'Montserrat', Arial, sans-serif;
    }
    .subtitle {
        color: #6d6f8d;
        margin-bottom: 2.2em;
        font-size: 1.05em;
    }
    form {
        background: #f0f2ff;
        border-radius: 12px;
        padding: 1em 1.2em;
        margin-bottom: 1.3em;
        box-shadow: 0 1px 4px 0 rgba(78,84,200,0.04);
    }
    label {
        display: block;
        text-align: left;
        margin: 0.5em 0 0.2em;
        font-size: 1em;
        font-weight: 500;
    }
    input[type="text"], input[type="password"] {
        width: 100%;
        padding: 0.6em 0.9em;
        border: 1px solid #a6a8be;
        border-radius: 7px;
        margin-bottom: 1em;
        font-size: 1em;
        background: #fff;
        box-sizing: border-box;
        outline: none;
        transition: border 0.2s;
    }
    input[type="text"]:focus, input[type="password"]:focus {
        border: 1.7px solid #4e54c8;
        background: #f9f8ff;
    }
    input[type="submit"] {
        background: linear-gradient(90deg,#4e54c8 30%,#8f94fb 100%);
        color: #fff;
        border: none;
        border-radius: 7px;
        font-size: 1.1em;
        padding: 0.7em 1.6em;
        margin-top: 0.2em;
        cursor: pointer;
        font-family: 'Montserrat', Arial, sans-serif;
        font-weight: 600;
        letter-spacing: 0.05em;
        transition: background 0.25s, box-shadow 0.25s;
        box-shadow: 0 2px 16px 0 rgba(78,84,200,0.09);
    }
    input[type="submit"]:hover {
        background: linear-gradient(90deg,#3840d4 20%,#8f94fb 100%);
        box-shadow: 0 4px 24px 0 rgba(78,84,200,0.17);
    }
    .section-title {
        color: #4e54c8;
        margin-top: 1.7em;
        font-size: 1.22em;
        font-weight: 700;
    }
    .flash {
        list-style: none;
        padding: 0.8em 0 0.1em 0;
        margin-bottom: 0.7em;
    }
    .flash li {
        background: linear-gradient(90deg,#ffecd2 0%,#fcb69f 100%);
        color: #b02020;
        border-radius: 6px;
        padding: 0.6em 0.8em;
        margin-bottom: 0.6em;
        font-size: 1em;
        border-left: 3.5px solid #fa6d6d;
        box-shadow: 0 0 4px 0 rgba(250,109,109,0.09);
        text-align: left;
    }
    .decrypted-box {
        background: #f2fff6;
        border: 2px solid #28d39a;
        color: #187a5b;
        font-size: 1.13em;
        border-radius: 7px;
        padding: 1.1em 0.9em;
        margin: 1.1em 0 0.6em 0;
        box-shadow: 0 0 6px 0 rgba(40,211,154,0.08);
    }
    .credit-card-img {
        width: 63px;
        vertical-align: middle;
        margin-right: 0.7em;
        margin-bottom: 0.1em;
        filter: drop-shadow(0 2px 10px #3840d466);
        border-radius: 8px;
    }
    .footer {
        margin-top: 2.6em;
        color: #888;
        font-size: 0.97em;
        opacity: 0.85;
        letter-spacing: 0.01em;
    }
    @media (max-width: 600px) {
        .container { max-width: 97vw; padding: 1.3em 0.3em 1em 0.3em; }
        h1 { font-size: 1.3em; }
        .section-title { font-size: 1em; }
    }
    </style>
</head>
<body>
    <div class="container">
        <img class="header-img" src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" alt="Security Icon"/>
        <h1>
            <img class="credit-card-img" src="https://cdn-icons-png.flaticon.com/512/633/633611.png" alt="Credit Card Icon"/>
            Secure Credit Card Vault
        </h1>
        <div class="subtitle">Your cards are encrypted and protected in the cloud<br>
        <span style="color:#187a5b;font-size:0.98em;">AES-256 Encryption | Local Storage | Access Control</span>
        </div>

        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <ul class="flash">
            {% for message in messages %}
              <li>{{ message|safe }}</li>
            {% endfor %}
            </ul>
          {% endif %}
        {% endwith %}

        <div class="section-title">Encrypt & Store Card</div>
        <form action="{{ url_for('encrypt') }}" method="post" autocomplete="off">
            <label>Admin Token:</label>
            <input name="token" type="password" placeholder="Enter Admin Token">

            <label>Card ID:</label>
            <input name="card_id" required placeholder="Unique Card ID">

            <label>Card Number:</label>
            <input name="card_number" required placeholder="e.g., 4111 1111 1111 1111">

            <input type="submit" value="Encrypt & Store">
        </form>

        <div class="section-title">Decrypt Card</div>
        <form action="{{ url_for('decrypt') }}" method="post" autocomplete="off">
            <label>Admin Token:</label>
            <input name="token" type="password" placeholder="Enter Admin Token">

            <label>Card ID:</label>
            <input name="card_id" required placeholder="Unique Card ID">

            <input type="submit" value="Decrypt">
        </form>

        {% if decrypted %}
            <div class="decrypted-box">
                <strong>Decrypted Card Number:</strong><br>
                {{ decrypted }}
            </div>
        {% endif %}

        <div class="footer">
            <span>
                <img src="https://cdn-icons-png.flaticon.com/512/3064/3064197.png" alt="Cloud" width="23" style="vertical-align:middle;"> 
                Local-Powered Security — Project by <a href="https://github.com/manasa-09-tech" style="color:#4e54c8;text-decoration:none;">manasa-09-tech</a>
            </span>
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE, decrypted=None)

@app.route('/encrypt', methods=['POST'])
def encrypt():
    token = request.form.get("token")
    card_id = request.form.get("card_id")
    card_number = request.form.get("card_number")
    if token != ADMIN_TOKEN:
        flash("❌ Invalid admin token!")
        return redirect(url_for('index'))
    if not card_id or not card_number:
        flash("❗ Card ID and Card Number required!")
        return redirect(url_for('index'))
    try:
        encrypted = encrypt_card(card_number)
        store_to_local(card_id, encrypted)
        flash(f"✅ Card <b>{card_id}</b> encrypted and stored successfully!")
    except Exception as e:
        flash(f"Encryption/Storage error: {str(e)}")
    return redirect(url_for('index'))

@app.route('/decrypt', methods=['POST'])
def decrypt():
    token = request.form.get("token")
    card_id = request.form.get("card_id")
    if token != ADMIN_TOKEN:
        flash("❌ Invalid admin token!")
        return redirect(url_for('index'))
    if not card_id:
        flash("❗ Card ID required!")
        return redirect(url_for('index'))
    try:
        encrypted = retrieve_from_local(card_id)
        card_number = decrypt_card(encrypted)
        return render_template_string(HTML_TEMPLATE, decrypted=card_number)
    except Exception as e:
        flash(f"Decryption error or Card not found: {str(e)}")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)