import os
import random
import string
from flask_mail import Message
from datetime import datetime

def generate_otp():
    """Generates a 6-digit numeric OTP."""
    return str(random.randint(100000, 999999))

def generate_verification_token():
    """Generates a 32-character random string (kept for legacy support if needed)."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

def generate_card_number():
    """Generates a 12-digit numeric string for card numbers."""
    return ''.join(random.choices(string.digits, k=12))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def send_verification_email(mail_obj, email, otp, mail_username):
    """Sends the 6-digit OTP to the admin email."""
    try:
        msg = Message('Admin Login Verification (OTP)', sender=mail_username, recipients=[email])
        msg.body = f"Your One-Time Password (OTP) for Admin Login is: {otp}\n\nThis code is valid for this login attempt only. Do not share it."
        mail_obj.send(msg)
        return True
    except Exception as e:
        print(f"Mail Error: {e}")
        return False

def send_card_email(mail_obj, email, name, card_number, card_image_path, mail_username, shop_name):
    """Sends the generated card image to the customer."""
    try:
        msg = Message(f'Your Premium Card - {shop_name}', sender=mail_username, recipients=[email])
        msg.body = f"Dear {name},\n\nWelcome to {shop_name}!\n\nPlease find your digital Premium Card attached below.\n\nCard Number: {card_number}\n\nShow this QR/Barcode at the counter to avail discounts."
        
        # Attach the generated card image
        with open(card_image_path, 'rb') as fp:
            msg.attach(f"card_{card_number}.png", "image/png", fp.read())
            
        mail_obj.send(msg)
        return True
    except Exception as e:
        print(f"Mail Error: {e}")
        return False