import os
import secrets
import re
from flask import Flask, render_template_string, redirect, url_for, flash, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField
from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(16))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, "uploads")
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
csrf = CSRFProtect(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    email_confirmed = db.Column(db.Boolean, default=False)
    email_token = db.Column(db.String(24), nullable=True)
    failed_logins = db.Column(db.Integer, default=0)
    lockout_until = db.Column(db.DateTime, nullable=True)
    profile_pic = db.Column(db.String(120), nullable=True, default=None)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def strong_password(form, field):
    pw = field.data
    if (len(pw) < 8 or not re.search(r'[A-Za-z]', pw) or not re.search(r'\d', pw) or not re.search(r'[^A-Za-z0-9]', pw)):
        raise ValidationError('Password must be at least 8 characters long and contain letters, numbers, and symbols.')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(4, 40)])
    email = StringField('Email', validators=[InputRequired(), Email(), Length(1, 120)])
    password = PasswordField('Password', validators=[InputRequired(), strong_password])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(4, 40)])
    password = PasswordField('Password', validators=[InputRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(), Length(1, 120)])
    submit = SubmitField('Send Reset Link')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[InputRequired(), strong_password])
    confirm_password = PasswordField('Confirm New Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

from wtforms import BooleanField
class ProfileForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(), Length(1, 120)])
    current_password = PasswordField('Current Password')
    new_password = PasswordField('New Password')
    confirm_new_password = PasswordField('Confirm New Password', validators=[EqualTo('new_password', message='Passwords must match')])
    profile_pic = FileField('Change Profile Picture')
    remove_pic = BooleanField('Remove profile picture')
    submit = SubmitField('Update Profile')

def send_email(to, subject, body):
    print(f"\n=== Simulated Email to: {to} ===")
    print(f"Subject: {subject}")
    print(f"Body:\n{body}")
    print("=== End Simulated Email ===\n")

def send_email_verification(user):
    link = f'http://localhost:5000/confirm/{user.email_token}'
    send_email(user.email, "Verify your account", f"Click to verify your email: {link}")

def send_reset_email(user, token):
    link = f'http://localhost:5000/reset/{token}'
    send_email(user.email, "Reset your password", f"Reset your password: {link}")

def generate_token(length=24):
    return secrets.token_urlsafe(length)[:length]

def save_profile_pic(file_storage, user_id):
    if not file_storage:
        return None
    filename = secure_filename(f"user_{user_id}_{file_storage.filename}")
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file_storage.save(path)
    return filename

def remove_profile_pic_file(filename):
    if filename:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        except Exception:
            pass

@app.route('/profile_pic/<filename>')
def profile_pic(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# -- TEMPLATES --

AUTH_BASE = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>{{ title or 'Auth' }}</title>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
  <style>
    body {
      font-family: 'Poppins', sans-serif;
      margin: 0;
      min-height: 100vh;
      background: url('https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=1500&q=80') center/cover no-repeat fixed;
      transition: background 0.3s;
    }
    .bg-overlay {
      position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
      background: rgba(24,34,56,0.6);
      backdrop-filter: blur(6px);
      z-index: 0;
      transition: background 0.3s;
    }
    .center-card {
      position: absolute;
      top: 50%; left: 50%;
      transform: translate(-50%, -50%);
      background: rgba(255,255,255,0.15);
      border-radius: 32px;
      box-shadow: 0 8px 32px rgba(31,38,135,0.37);
      backdrop-filter: blur(10px);
      padding: 2.5rem 2rem 2rem 2rem;
      min-width: 330px;
      max-width: 400px;
      width: 90vw;
      z-index: 1;
      animation: fadeIn 1.1s cubic-bezier(.39,.575,.565,1) 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      transition: background 0.3s, color 0.3s;
    }
    form {
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translate(-50%, -42%);}
      to   { opacity: 1; transform: translate(-50%, -50%);}
    }
    .auth-title {
      font-weight: 600;
      font-size: 2rem;
      margin-bottom: 1.1rem;
      color: #2d6cdf;
      letter-spacing: 1px;
      text-align: center;
      transition: color 0.3s;
    }
    .input-group {
      position: relative;
      margin-bottom: 1.1rem;
      width: 100%;
    }
    .input-group input[type="file"] {
      padding-left: 0;
      background: transparent;
    }
    .input-group input {
      width: 100%;
      padding: 0.75rem 2.5rem 0.75rem 2.2rem;
      border-radius: 12px;
      border: none;
      background: rgba(255,255,255,0.85);
      font-size: 1rem;
      box-shadow: 0 1px 2px rgba(60,60,60,0.07);
      transition: box-shadow .2s, background 0.3s, color 0.3s;
      box-sizing: border-box;
      display: block;
      color: #222;
    }
    .input-group input:focus {
      outline: none;
      box-shadow: 0 2px 14px #a0b9f9;
    }
    .input-group .fa-solid, .input-group .fa-regular {
      position: absolute;
      left: 0.9rem;
      top: 50%;
      transform: translateY(-50%);
      color: #2d6cdfa0;
      font-size: 1.1rem;
    }
    .remove-profile-pic-row {
      display: flex;
      flex-direction: row;
      align-items: center;
      margin-top: 0.3rem;
      margin-bottom: 0.8rem;
      gap: 0.5em;
    }
    .remove-profile-pic-checkbox {
      accent-color: #d03c3c;
      width: 1.13em;
      height: 1.13em;
      margin-right: 0.45em;
      margin-bottom: 0;
      vertical-align: middle;
    }
    .remove-profile-pic-label {
      color: #d03c3c;
      cursor: pointer;
      font-size: 1.04rem;
      font-weight: 500;
      user-select: none;
      margin-bottom: 0;
      margin-right: 0.3em;
      vertical-align: middle;
      display: inline-block;
    }
    .btn-auth {
      width: 100%;
      padding: 0.7rem 0;
      border-radius: 12px;
      border: none;
      background: linear-gradient(90deg, #4388e9 0%, #3d6cf9 100%);
      color: #fff;
      font-weight: 600;
      font-size: 1.1rem;
      margin-bottom: 0.7rem;
      box-shadow: 0 2px 10px #43e97b44;
      cursor: pointer;
      transition: box-shadow .18s, transform .16s, background 0.3s, color 0.3s;
      margin-top: 0.5rem;
    }
    .btn-auth:hover { box-shadow: 0 4px 20px #38f9d744; transform: translateY(-2px);}
    .btn-alt {
      background: linear-gradient(90deg, #36d1c4 0%, #5b86e5 100%) !important;
    }
    .or-sep {
      text-align: center;
      margin: 1rem 0;
      color: #3d6cf9a0;
      font-weight: 500;
      width: 100%;
    }
    .alert { padding: 0.7rem 1rem; border-radius: 10px; margin-bottom: 0.6rem; width: 100%; box-sizing: border-box;}
    .alert-danger { background: #ffdbdb; color: #a32828;}
    .alert-info { background: #deeaff; color: #184298;}
    .footer-signature {
      text-align: center;
      color: #1a2738;
      font-size: 1.05rem;
      margin-top: 2.2rem;
      opacity: 1;
      width: 100%;
      font-weight: 600;
      letter-spacing: 0.03em;
      transition: color 0.3s;
      text-shadow: none;
    }
    .footer-signature .fa-code {
      color: #2d6cdfb0;
      margin-right: 0.4rem;
    }
    .home-btn-top {
      position: absolute;
      top: 16px;
      right: 90px;
      z-index: 2;
      border-radius: 20px;
      background: linear-gradient(90deg,#36d1c4,#5b86e5);
      color: #fff;
      font-weight: 600;
      padding: 0.48rem 1.3rem;
      border: none;
      box-shadow: 0 2px 10px #86e5ff44;
      font-size: 1rem;
      text-decoration: none;
      cursor: pointer;
      transition: box-shadow .18s, background .22s;
      display: inline-block;
    }
    .home-btn-top:hover {
      background: linear-gradient(90deg,#43e97b,#38f9d7);
      color: #fff;
      box-shadow: 0 6px 16px #38f9d744;
      text-decoration: none;
    }
    .theme-toggle-btn {
      position: absolute;
      top: 16px;
      right: 28px;
      z-index: 2;
      border-radius: 20px;
      background: #fff;
      color: #222;
      font-weight: 600;
      padding: 0.48rem 1.3rem;
      border: none;
      box-shadow: 0 2px 10px #86e5ff44;
      font-size: 1rem;
      text-decoration: none;
      cursor: pointer;
      transition: background 0.3s, color 0.3s;
      display: inline-block;
      outline: none;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .theme-toggle-btn .fa-moon, .theme-toggle-btn .fa-sun {
      font-size: 1.15em;
    }
    .theme-toggle-btn:active {
      filter: brightness(0.95);
    }
    @media (max-width: 600px) {
      .center-card { min-width: unset; padding: 1.3rem 0.5rem; }
      .home-btn-top { right: 80px; top: 10px; font-size:0.97rem; padding:0.42rem 1.1rem;}
      .theme-toggle-btn { right: 10px; top: 10px; font-size:0.97rem; padding:0.42rem 1.1rem;}
    }
    body.darkmode .bg-overlay {
      background: rgba(10,14,22,0.97);
    }
    body.darkmode .center-card {
      background: rgba(32, 40, 65, 0.93);
      color: #e3e3e3;
    }
    body.darkmode .auth-title {
      color: #8fc3ff;
    }
    body.darkmode .input-group input {
      background: rgba(22,27,38,0.95);
      color: #e3e3e3;
    }
    body.darkmode .input-group .fa-solid,
    body.darkmode .input-group .fa-regular {
      color: #8fc3ff;
    }
    body.darkmode .btn-auth {
      background: linear-gradient(90deg,#192f3e,#2d7be7) !important;
      color: #fff;
    }
    body.darkmode .btn-alt {
      background: linear-gradient(90deg,#2d7be7,#36d1c4) !important;
      color: #fff;
    }
    body.darkmode .alert-danger {
      background: #54353b;
      color: #ffd2d2;
    }
    body.darkmode .alert-info {
      background: #25344d;
      color: #8fc3ff;
    }
    body.darkmode .footer-signature {
      color: #b7c8ea;
    }
  </style>
</head>
<body>
  <div class="bg-overlay"></div>
  <a href="{{ url_for('index') }}" class="home-btn-top"><i class="fa fa-home"></i> Home</a>
  <button class="theme-toggle-btn" id="toggleThemeBtn" title="Switch theme" aria-label="Toggle light/dark mode">
    <i class="fa fa-moon" id="themeIcon"></i>
  </button>
  <div class="center-card">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for cat, msg in messages %}
          <div class="alert alert-{{'danger' if cat=='danger' else 'info'}}">{{ msg }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}
    {{ content|safe }}
    <div class="footer-signature">
      <i class="fa-solid fa-code"></i>
      This project was developed by <b>DY MANASA</b>
    </div>
  </div>
  <script>
    const themeBtn = document.getElementById('toggleThemeBtn');
    const themeIcon = document.getElementById('themeIcon');
    function setTheme(mode) {
      if(mode === "dark") {
        document.body.classList.add('darkmode');
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-sun');
        localStorage.setItem('theme','dark');
      } else {
        document.body.classList.remove('darkmode');
        themeIcon.classList.remove('fa-sun');
        themeIcon.classList.add('fa-moon');
        localStorage.setItem('theme','light');
      }
    }
    (function() {
      let mode = localStorage.getItem('theme');
      if(!mode) {
        mode = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      }
      setTheme(mode);
    })();
    themeBtn.onclick = function() {
      setTheme(document.body.classList.contains('darkmode') ? 'light' : 'dark');
    }
  </script>
</body>
</html>
'''

PROFILE_HTML = '''
<div class="auth-title">Your Profile</div>
<form method="POST" enctype="multipart/form-data">
  {{ form.hidden_tag() }}
  <div style="text-align:center; margin-bottom:1.2rem;">
    {% if current_user.profile_pic %}
      <img src="{{ url_for('profile_pic', filename=current_user.profile_pic) }}" style="width:90px;height:90px;border-radius:50%;border:2px solid #38f9d7;margin-bottom:10px;">
    {% else %}
      <img src="https://ui-avatars.com/api/?name={{ current_user.username }}&background=38f9d7&color=fff" style="width:90px;height:90px;border-radius:50%;border:2px solid #38f9d7;margin-bottom:10px;">
    {% endif %}
  </div>
  <div class="input-group"><i class="fa-solid fa-envelope"></i>{{ form.email(class_="form-control", placeholder="Email") }}</div>
  {% for error in form.email.errors %}<div class="alert alert-danger">{{ error }}</div>{% endfor %}
  <div class="input-group"><i class="fa-solid fa-lock"></i>{{ form.current_password(class_="form-control", placeholder="Current Password") }}</div>
  {% for error in form.current_password.errors %}<div class="alert alert-danger">{{ error }}</div>{% endfor %}
  <div class="input-group"><i class="fa-solid fa-lock"></i>{{ form.new_password(class_="form-control", placeholder="New Password") }}</div>
  {% for error in form.new_password.errors %}<div class="alert alert-danger">{{ error }}</div>{% endfor %}
  <div class="input-group"><i class="fa-solid fa-lock"></i>{{ form.confirm_new_password(class_="form-control", placeholder="Confirm New Password") }}</div>
  {% for error in form.confirm_new_password.errors %}<div class="alert alert-danger">{{ error }}</div>{% endfor %}
  <div class="input-group" style="margin-bottom:0;">
    <i class="fa-regular fa-image"></i>
    {{ form.profile_pic(class_="form-control") }}
  </div>
  {% if current_user.profile_pic %}
    <div class="remove-profile-pic-row">
      {{ form.remove_pic(class_="remove-profile-pic-checkbox") }}
      <label class="remove-profile-pic-label" for="remove_pic">Remove profile picture</label>
    </div>
  {% endif %}
  <button type="submit" class="btn-auth">Update Profile</button>
  <div style="text-align:center; margin-top:1rem; font-size:1rem;">
    <a href="{{ url_for('index') }}" style="color:#43e97b; font-weight:600;">Back to Home</a>
  </div>
</form>
'''

INDEX_HTML = '''
<div style="text-align:center;padding-top:0.3rem;">
  <div style="font-size:2.3rem;font-weight:700;color:#2d6cdf;margin-bottom:1.2rem;">Welcome to Your Modern Auth System</div>
  <p style="font-size:1.1rem;color:#222c;">A beautiful, secure, and professional authentication project.</p>
  {% if current_user.is_authenticated %}
    <div style="margin:2.5rem 0 1.5rem 0;">
      <a href="{{ url_for('profile') }}" class="btn-auth btn-alt" style="width:80%;max-width:400px;margin:0.7rem auto;display:block;">Profile</a>
      <a href="{{ url_for('logout') }}" class="btn-auth" style="width:80%;max-width:400px;margin:0.7rem auto;display:block;">Logout</a>
    </div>
  {% else %}
    <div style="margin:2.5rem 0 2rem 0;">
      <a href="{{ url_for('register') }}" class="btn-auth btn-alt" style="width:80%;max-width:400px;margin:0.7rem auto;display:block;">Register</a>
      <a href="{{ url_for('login') }}" class="btn-auth" style="width:80%;max-width:400px;margin:0.7rem auto;display:block;">Login</a>
    </div>
  {% endif %}
</div>
'''
LOGIN_HTML = '''
<div class="auth-title">Sign In</div>
<form method="POST">
  {{ form.hidden_tag() }}
  <div class="input-group"><i class="fa-solid fa-user"></i>{{ form.username(class_="form-control", placeholder="Username") }}</div>
  {% for error in form.username.errors %}<div class="alert alert-danger">{{ error }}</div>{% endfor %}
  <div class="input-group"><i class="fa-solid fa-lock"></i>{{ form.password(class_="form-control", placeholder="Password") }}</div>
  {% for error in form.password.errors %}<div class="alert alert-danger">{{ error }}</div>{% endfor %}
  <div class="mb-2" style="width:100%;">{{ form.remember() }} <label for="remember">Remember me</label></div>
  <a href="{{ url_for('forgot_password') }}" class="forgot-link">Forgot password?</a>
  <button type="submit" class="btn-auth">Login</button>
  <div style="text-align:center; margin-top:1rem; font-size:1rem;">
    Don't have an account? <a href="{{ url_for('register') }}" style="color:#43e97b; font-weight:600;">Register</a>
  </div>
</form>
'''
REGISTER_HTML = '''
<div class="auth-title">Create Account</div>
<form method="POST">
  {{ form.hidden_tag() }}
  <div class="input-group"><i class="fa-solid fa-user"></i>{{ form.username(class_="form-control", placeholder="Username") }}</div>
  {% for error in form.username.errors %}<div class="alert alert-danger">{{ error }}</div>{% endfor %}
  <div class="input-group"><i class="fa-solid fa-envelope"></i>{{ form.email(class_="form-control", placeholder="Email") }}</div>
  {% for error in form.email.errors %}<div class="alert alert-danger">{{ error }}</div>{% endfor %}
  <div class="input-group"><i class="fa-solid fa-lock"></i>{{ form.password(class_="form-control", placeholder="Password") }}</div>
  {% for error in form.password.errors %}<div class="alert alert-danger">{{ error }}</div>{% endfor %}
  <div class="input-group"><i class="fa-solid fa-lock"></i>{{ form.confirm_password(class_="form-control", placeholder="Confirm Password") }}</div>
  {% for error in form.confirm_password.errors %}<div class="alert alert-danger">{{ error }}</div>{% endfor %}
  <button type="submit" class="btn-auth btn-alt">Register</button>
  <div style="text-align:center; margin-top:1rem; font-size:1rem;">
    Already have an account? <a href="{{ url_for('login') }}" style="color:#2d6cdf; font-weight:600;">Login</a>
  </div>
</form>
'''
FORGOT_HTML = '''
<div class="auth-title">Reset Password</div>
<form method="POST">
  {{ form.hidden_tag() }}
  <div class="input-group"><i class="fa-solid fa-envelope"></i>{{ form.email(class_="form-control", placeholder="Email") }}</div>
  {% for error in form.email.errors %}<div class="alert alert-danger">{{ error }}</div>{% endfor %}
  <button type="submit" class="btn-auth btn-alt">Send Reset Link</button>
  <div style="text-align:center; margin-top:1rem; font-size:1rem;">
    <a href="{{ url_for('login') }}" style="color:#2d6cdf; font-weight:600;">Back to Login</a>
  </div>
</form>
'''
RESET_HTML = '''
<div class="auth-title">Set New Password</div>
<form method="POST">
  {{ form.hidden_tag() }}
  <div class="input-group"><i class="fa-solid fa-lock"></i>{{ form.password(class_="form-control", placeholder="New Password") }}</div>
  {% for error in form.password.errors %}<div class="alert alert-danger">{{ error }}</div>{% endfor %}
  <div class="input-group"><i class="fa-solid fa-lock"></i>{{ form.confirm_password(class_="form-control", placeholder="Confirm New Password") }}</div>
  {% for error in form.confirm_password.errors %}<div class="alert alert-danger">{{ error }}</div>{% endfor %}
  <button type="submit" class="btn-auth btn-alt">Reset Password</button>
  <div style="text-align:center; margin-top:1rem; font-size:1rem;">
    <a href="{{ url_for('login') }}" style="color:#2d6cdf; font-weight:600;">Back to Login</a>
  </div>
</form>
'''
NOTFOUND_HTML = '''
<div style="text-align:center;">
  <div style="font-size:2.3rem;font-weight:700;color:#ff8c00;margin-bottom:1.2rem;">404 Not Found</div>
  <img src="https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=600&q=80" style="max-width:320px;border-radius:1rem;">
  <div style="margin-top:1.7rem;">
    <a href="{{ url_for('index') }}" class="btn-auth btn-alt" style="font-size:1.03rem;">Go Home</a>
  </div>
</div>
'''

@app.route('/')
def index():
    return render_template_string(AUTH_BASE, title="Home", content=render_template_string(INDEX_HTML))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.email_token = generate_token(16)
        db.session.add(user)
        db.session.commit()
        send_email_verification(user)
        flash('Registration successful! Please check your email to verify your account.', 'info')
        return redirect(url_for('login'))
    return render_template_string(AUTH_BASE, title="Register", content=render_template_string(REGISTER_HTML, form=form))

@app.route('/confirm/<token>')
def confirm_email(token):
    user = User.query.filter_by(email_token=token).first_or_404()
    if user.email_confirmed:
        flash('Email already verified.', 'success')
    else:
        user.email_confirmed = True
        user.email_token = None
        db.session.commit()
        flash('Email verified successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == "POST":
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.lockout_until and datetime.utcnow() < user.lockout_until:
                flash(f'Account locked. Try again at {user.lockout_until}.', 'danger')
                return render_template_string(AUTH_BASE, title="Login", content=render_template_string(LOGIN_HTML, form=form))
            if user.check_password(form.password.data):
                if not user.email_confirmed:
                    flash('Please verify your email before logging in.', 'info')
                    return render_template_string(AUTH_BASE, title="Login", content=render_template_string(LOGIN_HTML, form=form))
                login_user(user, remember=form.remember.data)
                user.failed_logins = 0
                user.lockout_until = None
                db.session.commit()
                flash('You are successfully logged in.', 'info')
                return redirect(url_for('index'))
            else:
                user.failed_logins += 1
                if user.failed_logins >= 5:
                    user.lockout_until = datetime.utcnow() + timedelta(minutes=10)
                    flash('Too many failed attempts. Account locked for 10 minutes.', 'danger')
                else:
                    flash('Invalid credentials.', 'danger')
                db.session.commit()
        else:
            flash('Invalid credentials.', 'danger')
    return render_template_string(AUTH_BASE, title="Login", content=render_template_string(LOGIN_HTML, form=form))

@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = generate_token(16)
            user.email_token = token
            db.session.commit()
            send_reset_email(user, token)
        flash('If this email is registered, a reset link has been sent.', 'info')
        return redirect(url_for('login'))
    return render_template_string(AUTH_BASE, title="Forgot Password", content=render_template_string(FORGOT_HTML, form=form))

@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(email_token=token).first_or_404()
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.email_token = None
        db.session.commit()
        flash('Password reset successful! Please login with your new password.', 'success')
        return redirect(url_for('login'))
    return render_template_string(AUTH_BASE, title="Reset Password", content=render_template_string(RESET_HTML, form=form))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if request.method == "POST":
        if form.validate_on_submit():
            # Remove profile picture if requested
            if form.remove_pic.data and current_user.profile_pic:
                remove_profile_pic_file(current_user.profile_pic)
                current_user.profile_pic = None
                flash("Profile picture removed.", "success")
            # Profile pic upload
            elif form.profile_pic.data:
                filename = save_profile_pic(form.profile_pic.data, current_user.id)
                if filename:
                    # Remove old pic
                    if current_user.profile_pic:
                        remove_profile_pic_file(current_user.profile_pic)
                    current_user.profile_pic = filename
                    flash("Profile picture updated.", "success")
            # Email update
            if form.email.data != current_user.email:
                if User.query.filter_by(email=form.email.data).first():
                    flash("Email already in use.", "danger")
                else:
                    current_user.email = form.email.data
                    current_user.email_confirmed = False
                    current_user.email_token = generate_token(16)
                    send_email_verification(current_user)
                    flash("Email update requested. Please verify your new email.", "info")
            # Password update
            if form.current_password.data and form.new_password.data:
                if not current_user.check_password(form.current_password.data):
                    flash("Current password is incorrect.", "danger")
                elif len(form.new_password.data) < 8:
                    flash("New password is too short.", "danger")
                else:
                    current_user.set_password(form.new_password.data)
                    flash("Password updated successfully.", "success")
            db.session.commit()
            return redirect(url_for('profile'))
    return render_template_string(AUTH_BASE, title="Profile", content=render_template_string(PROFILE_HTML, form=form))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    return render_template_string(AUTH_BASE, title="404 Not Found", content=NOTFOUND_HTML), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)