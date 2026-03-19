from flask import Flask, render_template, send_from_directory, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import pandas as pd
import json
import smtplib
import os
import re
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'super_secret_marketing_key'

# --- Authentication Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in or sign up to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- User Management logic ---
USERS_FILE = 'users.json'

def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def validate_password(password):
    if len(password) < 8: return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password): return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password): return False, "Password must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password): return False, "Password must contain at least one number."
    return True, ""

def send_emails(user_name, user_email, inquiry_type, message):
    """
    Sends two emails:
    1. Notification to the Admin.
    2. Confirmation/Auto-reply to the User.
    """
    admin_email = "dholesneha29@gmail.com"
    sender_email = os.environ.get('EMAIL_ADDRESS', admin_email)
    sender_password = os.environ.get('EMAIL_PASSWORD', '')

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- 1. Admin Email ---
    admin_msg = MIMEMultipart()
    admin_msg['From'] = sender_email
    admin_msg['To'] = admin_email
    admin_msg['Subject'] = f"New Feedback Received: {inquiry_type.title()}"
    
    admin_body = f"""New Feedback Received

Name: {user_name}
Email: {user_email}
Type: {inquiry_type}
Date & Time: {current_time}

Message:
{message}
"""
    admin_msg.attach(MIMEText(admin_body, 'plain'))

    # --- 2. User Auto-Reply Email ---
    user_msg = MIMEMultipart()
    user_msg['From'] = sender_email
    user_msg['To'] = user_email
    user_msg['Subject'] = "Thank You for Your Feedback - CampaignOptimizer"
    
    user_body = f"""Hi {user_name},

Thank you for reaching out to us regarding '{inquiry_type}'. We have received your message and our team will review it shortly!

For your records, here is a copy of your message submitted on {current_time}:
"{message}"

Best regards,
CampaignOptimizer Team
"""
    user_msg.attach(MIMEText(user_body, 'plain'))

    # Display emails in the console (for demo/logging purposes without breaking the API)
    print("\n" + "="*40)
    print("📧 [EMAIL INTERCEPTOR LOG]")
    print(f"To: ADMIN ({admin_email})")
    print(admin_body)
    print("-" * 40)
    print(f"To: USER ({user_email})")
    print(user_body)
    print("="*40 + "\n")

    # If the environment variables exist securely, send the real emails
    if sender_password and sender_password != 'your_gmail_app_password_here':
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, admin_email, admin_msg.as_string())
            server.sendmail(sender_email, user_email, user_msg.as_string())
            server.quit()
            print("✅ Live Emails successfully dispatched via SMTP.")
        except Exception as e:
            print(f"❌ SMTP Send Failed: {e}")
            # We don't raise the error so the API response isn't broken
    else:
        print("⚠️ Real emails were NOT sent. To enable live sending, supply EMAIL_ADDRESS and EMAIL_PASSWORD environment variables.")

# Basic routing to serve images from the current directory
@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory('.', filename)

def load_data():
    try:
        df = pd.read_csv('marketing_data.csv')
        channel_agg = df.groupby('Channel').agg({
            'Cost/Ad Spend': 'sum',
            'Revenue Generated': 'sum',
            'Customer Acquired': 'sum',
            'Conversions': 'sum',
            'Clicks': 'sum'
        }).reset_index()

        channel_agg['CAC'] = channel_agg['Cost/Ad Spend'] / channel_agg['Customer Acquired']
        channel_agg['ROI'] = (channel_agg['Revenue Generated'] - channel_agg['Cost/Ad Spend']) / channel_agg['Cost/Ad Spend']
        channel_agg['CR'] = channel_agg['Conversions'] / channel_agg['Clicks']
        
        channel_agg_sorted = channel_agg.sort_values(by='CAC')
        
        top_channels = channel_agg_sorted.head(3).to_dict(orient='records')
        bottom_channels = channel_agg_sorted.tail(3).to_dict(orient='records')
        
        total_spend = df['Cost/Ad Spend'].sum()
        total_revenue = df['Revenue Generated'].sum()
        total_roi = (total_revenue - total_spend) / total_spend
        
        stats = {
            'total_spend': f"${total_spend:,.2f}",
            'total_revenue': f"${total_revenue:,.2f}",
            'total_roi': f"{total_roi * 100:.2f}%",
            'total_records': len(df)
        }
        
        return top_channels, bottom_channels, stats
    except Exception as e:
        print("Data loading error:", e)
        return [], [], {}


@app.route('/')
def landing():
    return render_template('landing.html', active_page='home')

@app.route('/dashboard')
@login_required
def dashboard():
    top, bottom, stats = load_data()
    return render_template('dashboard.html', top_channels=top, bottom_channels=bottom, stats=stats, active_page='dashboard')

@app.route('/visualizations')
@login_required
def visualizations():
    return render_template('visualizations.html', active_page='visualizations')

@app.route('/recommendations')
@login_required
def recommendations():
    top, bottom, stats = load_data()
    return render_template('recommendations.html', top_channels=top, bottom_channels=bottom, active_page='recommendations')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        users = load_users()
        
        if email in users:
            flash('Account already exists. Please log in.', 'error')
            return redirect(url_for('login'))
            
        is_valid, msg = validate_password(password)
        if not is_valid:
            flash(msg, 'error')
            return render_template('signup.html', active_page='signup')
            
        users[email] = {
            'name': name,
            'password': generate_password_hash(password),
            'role': role
        }
        save_users(users)
        
        session['logged_in'] = True
        session['user_email'] = email
        session['user_role'] = role
        flash('Account created successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('signup.html', active_page='signup')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        users = load_users()
        user = users.get(email)
        
        if not user or not check_password_hash(user['password'], password):
            flash('Invalid email or password.', 'error')
            return render_template('login.html', active_page='login')
            
        if user['role'] != role:
            flash(f'Account is registered as {user["role"]}, not {role}.', 'error')
            return render_template('login.html', active_page='login')
            
        session['logged_in'] = True
        session['user_email'] = email
        session['user_role'] = role
        flash('Successfully logged in!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('login.html', active_page='login')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('landing'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    success = False
    error_msg = None
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        inquiry_type = request.form.get('type')
        message = request.form.get('message')
        
        try:
            # Trigger modular email function
            send_emails(name, email, inquiry_type, message)
            success = True
        except Exception as e:
            print(f"Exception caught in contact route: {e}")
            # Ensure the user still sees success message or a graceful fallback
            success = True 
            
    return render_template('contact.html', active_page='contact', success=success, error_msg=error_msg)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
