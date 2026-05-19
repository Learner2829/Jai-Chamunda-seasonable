
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import random
import string
import qrcode
import io
from io import BytesIO
from datetime import datetime
from config import Config
from utils.helpers import generate_verification_token, generate_card_number, allowed_file, send_verification_email, send_card_email, generate_otp

# --- IMAGE GENERATION IMPORTS ---
from PIL import Image, ImageDraw, ImageFont, ImageChops
import barcode
from barcode.writer import ImageWriter

# --- PDF IMPORTS ---
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether
from reportlab.lib import colors
from reportlab.lib.units import inch

app = Flask(__name__)
app.config.from_object(Config)

# ==========================================
#   GLOBAL SHOP SETTINGS & DEFAULTS
# ==========================================
SHOP_NAME = "New Ambika Seasonable's"

# Default Card Layout Settings (Position of the Number)
CARD_SETTINGS = {
    'front_num_x': 90,
    'front_num_y': 200,
    'front_font_size': 48
}

@app.context_processor
def inject_global_vars():
    return dict(shop_name=SHOP_NAME)

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join('static', 'images'), exist_ok=True) 
os.makedirs(os.path.join('static', 'cards'), exist_ok=True) 

# Initialize extensions
mysql = MySQL(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'
login_manager.login_message_category = 'info'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, email, is_admin=False):
        self.id = id
        self.email = email
        self.is_admin = is_admin

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, email, is_admin FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    if user:
        return User(user[0], user[1], user[2])
    return None

# ==========================================
#   DATABASE INITIALIZATION
# ==========================================
def init_db():
    try:
        cur = mysql.connection.cursor()
        
        # Tables Creation (Users, Posts, Cards, Visits)
        cur.execute('''CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, email VARCHAR(120) UNIQUE NOT NULL, password VARCHAR(255) NOT NULL, name VARCHAR(100), address TEXT, phone VARCHAR(20), is_admin BOOLEAN DEFAULT FALSE, email_verified BOOLEAN DEFAULT FALSE, verification_token VARCHAR(100), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS posts (id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255) NOT NULL, description TEXT, image_path VARCHAR(255), discount DECIMAL(5,2), admin_id INT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (admin_id) REFERENCES users(id))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS premium_cards (id INT AUTO_INCREMENT PRIMARY KEY, user_id INT NULL, card_number VARCHAR(12) UNIQUE NOT NULL, qr_code_path VARCHAR(255), pdf_path VARCHAR(255), visits INT DEFAULT 0, total_discount DECIMAL(10,2) DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS visits (id INT AUTO_INCREMENT PRIMARY KEY, card_id INT, product_info TEXT, purchase_amount DECIMAL(10,2) DEFAULT 0.00, discount_applied DECIMAL(10,2), visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (card_id) REFERENCES premium_cards(id) ON DELETE CASCADE)''')

        # Auto-Migration logic
        try:
            cur.execute("ALTER TABLE premium_cards MODIFY user_id INT NULL")
            cur.execute("SELECT purchase_amount FROM visits LIMIT 1")
        except:
            try:
                cur.execute("ALTER TABLE visits ADD COLUMN purchase_amount DECIMAL(10,2) DEFAULT 0.00 AFTER product_info")
                cur.execute("ALTER TABLE visits MODIFY discount_applied DECIMAL(10,2)")
            except: pass
            
        # Create Admin
        cur.execute("SELECT * FROM users WHERE is_admin = TRUE")
        if not cur.fetchone():
            hashed_password = generate_password_hash('admin123')
            cur.execute("INSERT INTO users (email, password, name, is_admin, email_verified) VALUES (%s, %s, %s, %s, %s)", ('admin@shop.com', hashed_password, 'Admin', True, True))
        
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        print(f"DB Init Error: {e}")

# ==========================================
#   CARD GENERATOR FUNCTION (FIXED)
# ==========================================
def generate_card_image(name, card_number, preview_mode=False):
    basedir = os.path.abspath(os.path.dirname(__file__))
    output_folder = os.path.join(basedir, 'static', 'cards')
    image_folder = os.path.join(basedir, 'static', 'images')
    
    # Use Global Settings for Positioning
    global CARD_SETTINGS
    # fx = int(CARD_SETTINGS.get('front_num_x', 60))
    # fy = int(CARD_SETTINGS.get('front_num_y', 670))
    # f_size = int(CARD_SETTINGS.get('front_font_size', 48))

    fx= 136
    fy = 1000
    f_size = 200

    # Fixed positions for other elements
    barcode_w, barcode_h, barcode_x, barcode_y = 520, 280, 2100, 1200
    name_x, name_y, name_font_size = 80, 300, 60
    date_x, date_y, date_font_size = 2100, 1300, 60

    # 1. Load Images
    front_image_path = os.path.join(image_folder, 'Card_front.png')
    back_image_path = os.path.join(image_folder, 'Card_back.png')
    
    try: front_image = Image.open(front_image_path).convert("RGBA")
    except: front_image = Image.new('RGBA', (1000, 630), (20, 50, 150, 255))
    
    try: back_image = Image.open(back_image_path).convert("RGBA")
    except: back_image = Image.new('RGBA', (1000, 630), (200, 200, 200, 255))

    # Data
    display_card_num = "  ".join([card_number[i:i+4] for i in range(0, len(card_number), 4)])
    generate_date_text = "VALID THRU: " + datetime.now().strftime("%m/%y")
    display_name = name.upper() if name else ""

    # Fonts
    text_color_gold = (235, 215, 120, 255)   
    text_color_white = (240, 240, 240, 255)  
    shadow_color = (0, 0, 0, 150)            
    
    try:
        font_front_num = ImageFont.truetype("courbd.ttf", f_size)
        font_name = ImageFont.truetype("arialbd.ttf", name_font_size)
        font_date = ImageFont.truetype("arial.ttf", date_font_size)
        font_barcode_text = ImageFont.truetype("arial.ttf", 24)
    except:
        font_front_num = ImageFont.load_default()
        font_name = ImageFont.load_default()
        font_date = ImageFont.load_default()
        font_barcode_text = ImageFont.load_default()

    # --- DRAW FRONT ---
    front_layer = Image.new('RGBA', front_image.size, (255, 255, 255, 0))
    draw_front = ImageDraw.Draw(front_layer)

    # 1. Number (Using Dynamic Settings fx, fy)
    draw_front.text((fx + 2, fy + 2), display_card_num, font=font_front_num, fill=shadow_color)
    draw_front.text((fx, fy), display_card_num, font=font_front_num, fill=text_color_gold)
    
    # 2. Date & Name
    draw_front.text((date_x, date_y), generate_date_text, font=font_date, fill=text_color_white)
    draw_front.text((name_x + 1, name_y + 1), display_name, font=font_name, fill=shadow_color)
    draw_front.text((name_x, name_y), display_name, font=font_name, fill=text_color_gold)

    front_image = Image.alpha_composite(front_image, front_layer)

    # --- DRAW BACK ---
    back_layer = Image.new('RGBA', back_image.size, (255, 255, 255, 0))
    draw_back = ImageDraw.Draw(back_layer)

    # Use fixed layout for back for now, or add more settings later
    draw_back.text((60, 200), display_card_num, font=font_front_num, fill=text_color_white)
    back_image = Image.alpha_composite(back_image, back_layer)

    # Barcode logic
    rv = io.BytesIO()
    Code128 = barcode.get_barcode_class('code128')
    my_barcode = Code128(card_number, writer=ImageWriter())
    my_barcode.write(rv, options={'write_text': False, 'module_height': 10.0, 'quiet_zone': 1.0})
    rv.seek(0)
    barcode_raw = Image.open(rv).convert("RGBA")
    
    final_barcode = barcode_raw.resize((barcode_w, barcode_h), Image.Resampling.LANCZOS)
    back_image.paste(final_barcode, (barcode_x, barcode_y))

    # --- RETURN LOGIC ---
    if preview_mode:
        img_io = BytesIO()
        front_image.save(img_io, 'PNG')
        img_io.seek(0)
        return img_io

    front_filename = f"card_{card_number}.png"
    back_filename = f"card_{card_number}_back.png"
    
    front_image.save(os.path.join(output_folder, front_filename))
    back_image.save(os.path.join(output_folder, back_filename))
    
    return front_filename, os.path.join(output_folder, front_filename)

# ==========================================
#   ADJUST CARD ROUTE (NEW)
# ==========================================
@app.route('/admin/adjust-card', methods=['GET', 'POST'])
@login_required
def adjust_card():
    if not current_user.is_admin: return redirect(url_for('index'))
    global CARD_SETTINGS
    if request.method == 'POST':
        CARD_SETTINGS['front_num_x'] = int(request.form.get('front_num_x', 60))
        CARD_SETTINGS['front_num_y'] = int(request.form.get('front_num_y', 200))
        CARD_SETTINGS['front_font_size'] = int(request.form.get('front_font_size', 48))
        flash('Settings updated! Check the preview.', 'success')
    return render_template('admin/adjust_card.html', settings=CARD_SETTINGS)

@app.route('/admin/card-preview')
@login_required
def card_preview():
    # Random number for preview
    return send_file(generate_card_image("Preview User", "123456789012", preview_mode=True), mimetype='image/png')

# ==========================================
#   EXISTING ROUTES
# ==========================================
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT p.*, u.name as admin_name FROM posts p JOIN users u ON p.admin_id = u.id ORDER BY p.created_at DESC")
    posts = cur.fetchall()
    cur.close()
    return render_template('index.html', posts=posts)

@app.route('/posts')
def posts():
    cur = mysql.connection.cursor()
    cur.execute("SELECT p.*, u.name as admin_name FROM posts p JOIN users u ON p.admin_id = u.id ORDER BY p.created_at DESC")
    posts = cur.fetchall()
    cur.close()
    return render_template('posts.html', posts=posts)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND is_admin = TRUE", (email,))
        admin = cur.fetchone()
        cur.close()
        if admin and check_password_hash(admin[2], password):
            otp = generate_otp()
            cur = mysql.connection.cursor()
            cur.execute("UPDATE users SET verification_token = %s WHERE id = %s", (otp, admin[0]))
            mysql.connection.commit()
            cur.close()
            if send_verification_email(mail, admin[1], otp, app.config['MAIL_USERNAME']):
                session['otp_email'] = admin[1]
                return redirect(url_for('verify_otp_page'))
            else: flash('Email failed.', 'danger')
        else: flash('Invalid credentials', 'danger')
    return render_template('admin/login.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp_page():
    if 'otp_email' not in session: return redirect(url_for('admin_login'))
    if request.method == 'POST':
        entered_otp = request.form['otp']
        email = session['otp_email']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND verification_token = %s AND is_admin = TRUE", (email, entered_otp))
        user = cur.fetchone()
        if user:
            cur.execute("UPDATE users SET verification_token = NULL WHERE id = %s", (user[0],))
            mysql.connection.commit()
            cur.close()
            login_user(User(user[0], user[1], user[6]))
            session.pop('otp_email', None)
            return redirect(url_for('admin_dashboard'))
        else: flash('Invalid OTP', 'danger')
    return render_template('admin/verify_otp.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin: return redirect(url_for('index'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE is_admin = FALSE")
    total_users = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM posts")
    total_posts = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM premium_cards")
    total_cards = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM visits WHERE DATE(visit_date) = CURDATE()")
    today_visits = cur.fetchone()[0]
    cur.close()
    return render_template('admin/dashboard.html', total_users=total_users, total_posts=total_posts, total_cards=total_cards, today_visits=today_visits)

@app.route('/admin/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    if not current_user.is_admin: return redirect(url_for('index'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        discount = request.form.get('discount', 0)
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = filename
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO posts (title, description, image_path, discount, admin_id) VALUES (%s, %s, %s, %s, %s)", (title, description, image_path, discount, current_user.id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/add_post.html')

@app.route('/admin/generate-empty', methods=['POST'])
@login_required
def generate_empty_card():
    if not current_user.is_admin: return redirect(url_for('index'))
    card_number = generate_card_number()
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(card_number)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_filename = f"qr_{card_number}.png"
    qr_path = os.path.join(app.config['UPLOAD_FOLDER'], qr_filename)
    qr_img.save(qr_path)
    card_filename, _ = generate_card_image("", card_number)
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO premium_cards (user_id, card_number, qr_code_path, pdf_path) VALUES (NULL, %s, %s, %s)", (card_number, qr_filename, card_filename))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('connect_card'))

@app.route('/admin/connect-card', methods=['GET', 'POST'])
@login_required
def connect_card():
    if not current_user.is_admin: return redirect(url_for('index'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT card_number FROM premium_cards WHERE user_id IS NULL ORDER BY created_at DESC")
    empty_cards = cur.fetchall()
    cur.execute("SELECT pc.card_number, u.name, u.email, pc.created_at FROM premium_cards pc JOIN users u ON pc.user_id = u.id WHERE u.is_admin = FALSE ORDER BY pc.created_at DESC LIMIT 10")
    recent_connections = cur.fetchall()
    if request.method == 'POST':
        card_number = request.form['card_number']
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        phone = request.form.get('phone', '')
        cur.execute("SELECT id, user_id FROM premium_cards WHERE card_number = %s", (card_number,))
        card_row = cur.fetchone()
        if card_row and card_row[1] is None:
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            existing_user = cur.fetchone()
            if existing_user:
                user_id = existing_user[0]
                cur.execute("UPDATE users SET name=%s, address=%s, phone=%s WHERE id=%s", (name, address, phone, user_id))
            else:
                temp_pass = generate_password_hash(phone if phone else "123456")
                cur.execute("INSERT INTO users (email, password, name, address, phone, email_verified, is_admin) VALUES (%s, %s, %s, %s, %s, TRUE, FALSE)", (email, temp_pass, name, address, phone))
                user_id = cur.lastrowid
            new_filename, new_fullpath = generate_card_image(name, card_number)
            cur.execute("UPDATE premium_cards SET user_id = %s, pdf_path = %s WHERE card_number = %s", (user_id, new_filename, card_number))
            mysql.connection.commit()
            send_card_email(mail, email, name, card_number, new_fullpath, app.config['MAIL_USERNAME'], SHOP_NAME)
            flash('Connected successfully', 'success')
        else: flash('Invalid or used card', 'danger')
        return redirect(url_for('connect_card'))
    return render_template('admin/connect_card.html', empty_cards=empty_cards, recent_connections=recent_connections)

@app.route('/card/view/<filename>')
@login_required
def view_generated_card(filename):
    return send_file(os.path.join(app.root_path, 'static', 'cards', filename), mimetype='image/png')

@app.route('/admin/scan-card', methods=['GET', 'POST'])
@login_required
def scan_card():
    if not current_user.is_admin: return redirect(url_for('index'))
    if request.method == 'POST':
        card_number = request.form['card_number']
        product_info = request.form['product_info']
        total_amount = float(request.form.get('total_amount', 0))
        discount_percent = float(request.form.get('discount', 0))
        actual_discount_value = (total_amount * discount_percent) / 100
        cur = mysql.connection.cursor()
        cur.execute("SELECT pc.id, pc.user_id, u.name FROM premium_cards pc JOIN users u ON pc.user_id = u.id WHERE pc.card_number = %s", (card_number,))
        card = cur.fetchone()
        if card:
            cur.execute("INSERT INTO visits (card_id, product_info, purchase_amount, discount_applied) VALUES (%s, %s, %s, %s)", (card[0], product_info, total_amount, actual_discount_value))
            cur.execute("UPDATE premium_cards SET visits = visits + 1, total_discount = total_discount + %s WHERE id = %s", (actual_discount_value, card[0]))
            mysql.connection.commit()
            flash(f'Saved: {actual_discount_value}', 'success')
        else: flash('Invalid card', 'danger')
        cur.close()
    return render_template('admin/scan_card.html')

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin: return redirect(url_for('index'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT u.id, u.name, u.email, u.address, u.phone, u.created_at, pc.card_number, COALESCE(pc.visits, 0), COALESCE(pc.total_discount, 0.00) FROM users u LEFT JOIN premium_cards pc ON u.id = pc.user_id WHERE u.is_admin = FALSE ORDER BY u.created_at DESC")
    users = cur.fetchall()
    cur.execute("SELECT pc.user_id, v.visit_date, v.product_info, v.purchase_amount, v.discount_applied FROM visits v JOIN premium_cards pc ON v.card_id = pc.id ORDER BY v.visit_date DESC")
    all_visits = cur.fetchall()
    cur.close()
    visits_by_user = {}
    for v in all_visits:
        u_id = v[0]
        if u_id not in visits_by_user: visits_by_user[u_id] = []
        visits_by_user[u_id].append(v)
    return render_template('admin/users.html', users=users, visits_by_user=visits_by_user)

@app.route('/admin/download-users-pdf')
@login_required
def download_users_pdf():
    if not current_user.is_admin: return redirect(url_for('index'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT u.id, u.name, u.email, u.address, u.phone, u.created_at, pc.card_number, COALESCE(pc.visits, 0), COALESCE(pc.total_discount, 0.00) FROM users u LEFT JOIN premium_cards pc ON u.id = pc.user_id WHERE u.is_admin = FALSE ORDER BY u.created_at DESC")
    users = cur.fetchall()
    cur.execute("SELECT pc.user_id, v.visit_date, v.product_info, v.purchase_amount, v.discount_applied FROM visits v JOIN premium_cards pc ON v.card_id = pc.id ORDER BY v.visit_date DESC")
    all_visits = cur.fetchall()
    cur.close()
    visits_map = {}
    for v in all_visits:
        u_id = v[0]
        if u_id not in visits_map: visits_map[u_id] = []
        visits_map[u_id].append(v)
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    story = [Paragraph(f"{SHOP_NAME} - Report", styles['Heading1']), Spacer(1, 20)]
    for user in users:
        user_id, user_name = user[0], user[1]
        t1 = Table([[Paragraph(f"Customer: {user_name}", styles['Normal']), Paragraph(f"Card: {user[6]}", styles['Normal'] )], [Paragraph(f"Phone: {user[4]}", styles['Normal']), Paragraph(f"Savings: {user[8]}", styles['Normal'])]], colWidths=[3.5*inch, 3.5*inch])
        t1.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke)]))
        story.append(t1)
        story.append(Spacer(1, 5))
        if user_id in visits_map:
            v_data = [['Date', 'Product', 'Amount', 'Discount']]
            for v in visits_map[user_id]:
                v_data.append([v[1].strftime('%d/%m'), Paragraph(v[2], styles['BodyText']), f"{v[3]}", f"{v[4]}"])
            t2 = Table(v_data, colWidths=[1*inch, 4*inch, 1*inch, 1*inch])
            t2.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.25, colors.lightgrey), ('BACKGROUND', (0,0), (-1,0), colors.black), ('TEXTCOLOR', (0,0), (-1,0), colors.white)]))
            story.append(t2)
        story.append(Spacer(1, 20))
    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='report.pdf', mimetype='application/pdf')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin/create-card', methods=['GET', 'POST'])
@login_required
def create_card():
    if not current_user.is_admin: return redirect(url_for('index'))
    if request.method == 'POST':
        # ... (logic same as connect-card but manual)
        return redirect(url_for('admin_dashboard')) # Simplified for brevity as logic is duplicate of connect
    return render_template('admin/create_card.html')

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)