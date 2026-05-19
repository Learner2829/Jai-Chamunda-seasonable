# Jai Chamunda Seasonable - Retail CRM & Loyalty System 🛍️

A comprehensive, full-stack web application developed to digitize retail operations, manage inventory promotions, and automate a premium customer loyalty program for a seasonal retail business. 

This system allows administrators to track high-value customer interactions, dynamically generate custom loyalty cards with integrated barcodes/QR codes, and analyze purchase patterns through automated PDF reporting.

## ✨ Key Features

* **Automated Loyalty Card Generation:** Dynamically generates personalized premium customer cards using Python Imaging Library (Pillow). Each card is embedded with unique Code128 barcodes and QR codes for seamless in-store scanning.
* **Customer & Visit Tracking:** Securely maps unique card IDs to customer profiles in a relational database, automatically calculating percentage-based discounts and tracking cumulative savings over time.
* **Automated PDF Analytics:** Utilizes ReportLab to generate automated, downloadable PDF reports detailing customer visit frequencies, total purchase amounts, and business performance metrics.
* **Secure Admin Dashboard:** Features role-based access control (RBAC), secure password hashing (Werkzeug), and dynamic OTP email verification for secure administrative access.
* **Promotional Content Management:** Allows admins to create, manage, and display promotional posts and seasonal discounts to end-users.

## 🛠️ Tech Stack

* **Backend:** Python, Flask
* **Database:** MySQL (Flask-MySQLdb)
* **Authentication & Security:** Flask-Login, Werkzeug
* **Image Processing:** Pillow (PIL), python-barcode, qrcode
* **Document Generation:** ReportLab
* **Frontend:** HTML5, CSS3, Jinja2 Templates

## 🚀 Installation & Setup

### Prerequisites
* Python 3.8+
* MySQL Server installed and running
* A valid Gmail account for sending OTPs and Customer Emails

### Steps

1. **Clone the repository**
   ```bash
   git clone [https://github.com/yourusername/Jai-Chamunda-seasonable.git](https://github.com/yourusername/Jai-Chamunda-seasonable.git)
   cd Jai-Chamunda-seasonable
