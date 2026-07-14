import os
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load variables from the local hidden .env file
load_dotenv('../../.env')

app = Flask(__name__)

# Allow connections from any local testing environment or GitHub Pages layout
CORS(app)

# Fetch secure configuration settings from environment memory
SMTP_SERVER = "://gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

# Check if environment variables exist before executing backend services
if not all([SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL]):
    print("\n[CRITICAL CONFIGURATION ERROR]")
    print("SENDER_EMAIL, SENDER_PASSWORD, or RECEIVER_EMAIL is missing from your hidden .env file.")
    print("Please fix your .env file layout before proceeding.\n")
    exit(1)

@app.route('/submit-form', methods=['POST'])
def handle_form():
    try:
        # Determine whether input format is sent as JSON or standard URL form payload
        if request.is_json:
            data = request.get_json()
            name = data.get('name')
            email = data.get('email')
            message = data.get('message')
        else:
            name = request.form.get('name')
            email = request.form.get('email')
            message = request.form.get('message')

        # Prevent empty or corrupted submissions from triggering system exceptions
        if not name or not email or not message:
            return jsonify({"status": "error", "message": "All text input boxes must be filled out!"}), 400

        # Construct structural layout for outbound mail notification
        email_body = f"New Contact Form Submission:\n\nName: {name}\nEmail: {email}\nMessage:\n{message}"
        msg = MIMEText(email_body)
        msg['Subject'] = f"Website Contact Form: {name}"
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL

        # Initialize network stream connection over Google secure TLS framework
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], msg.as_string())
        server.quit()

        return jsonify({"status": "success", "message": "Your message was sent successfully!"}), 200

    except smtplib.SMTPAuthenticationError:
        print("[SMTP AUTHENTICATION ERROR] Verification failed. Ensure your Google App Password is correct.")
        return jsonify({"status": "error", "message": "Internal configuration error linking to email provider."}), 500
    except Exception as error_details:
        print(f"[SERVER ROUTE CRASH] Technical details: {error_details}")
        return jsonify({"status": "error", "message": "Internal server processing failure."}), 500

if __name__ == '__main__':
    print("\n---------------------------------------------------------")
    print("Form Handler Backend Server successfully opened!")
    print("Listening for incoming messages on: http://127.0.0.1:5000")
    print("---------------------------------------------------------\n")
    app.run(host='127.0.0.1', port=5000, debug=True)
