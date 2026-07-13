import os
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# 1. Load the hidden local .env file variables into system environment
load_dotenv()

app = Flask(__name__)

# 2. Allow your GitHub Pages frontend to talk to this backend
# Replace '*' with your specific GitHub Pages URL later for better security
CORS(app, resources={r"/submit-form": {"origins": "*"}})

# 3. Pull configurations safely from system environment variables
SMTP_SERVER = "://gmail.com"  # Change if you do not use Gmail
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

# 4. Safety Fail-Safe: Stop immediately if keys are missing from your .env
if not all([SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL]):
    print("\n[CRITICAL ERROR] Execution halted!")
    print("Please ensure SENDER_EMAIL, SENDER_PASSWORD, and RECEIVER_EMAIL are set in your hidden .env file.\n")
    exit(1)


@app.route('/submit-form', methods=['POST'])
def handle_form():
    try:
        # Check if incoming request is standard HTML Form Data or JSON data
        if request.is_json:
            data = request.get_json()
            name = data.get('name')
            email = data.get('email')
            message = data.get('message')
        else:
            name = request.form.get('name')
            email = request.form.get('email')
            message = request.form.get('message')

        # Basic server-side input validation
        if not name or not email or not message:
            return jsonify({"status": "error", "message": "All fields are required!"}), 400

        # Construct the formal email text
        email_body = f"New Contact Form Submission:\n\nName: {name}\nEmail: {email}\nMessage:\n{message}"
        msg = MIMEText(email_body)
        msg['Subject'] = f"Website Contact Form: {name}"
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL

        # Open secure encrypted connection to Google SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Enforce TLS encryption
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, [RECEIVER_EMAIL], msg.as_string())
        server.quit()

        return jsonify({"status": "success", "message": "Your message was sent successfully!"}), 200

    except smtplib.SMTPAuthenticationError:
        print("[SMTP ERROR] Authentication failed. Check your Gmail App Password.")
        return jsonify({"status": "error", "message": "Email server authentication configuration issue."}), 500
    except Exception as e:
        print(f"[SERVER ERROR] Details: {e}")
        return jsonify({"status": "error", "message": "Internal server processing error."}), 500


if __name__ == '__main__':
    # Runs the server on localhost port 5000 for your local VS Code testing
    print(u"\u2705 Form Handler Server running on http://127.0.0.1:5000")
    app.run(port=5000, debug=True)
