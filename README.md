# User Authentication System

## Short Description
This project is a **modern user authentication system** built with Python and Flask. It features secure login, password encryption with bcrypt, account locking after multiple failed login attempts, and stores user data in **Google Sheets**.

---

## Installation / Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Bemine5Cent/User_Authentication.git
   cd User_Authentication

    Create a virtual environment (recommended):

python3 -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows

Install dependencies:

pip install -r requirements.txt

Set up Google Sheets credentials:

Your teacher or anyone running this project must create their own credentials.json:

    Go to the Google Cloud Console
    .

    Create a new project (or select an existing one).

    Navigate to APIs & Services > Credentials.

    Click Create Service Account and give it a name.

    Under the service account, create a key in JSON format.

    Download the JSON file and save it as credentials.json in the project root.

    Share your Google Sheet (where user data will be stored) with the service account email (found in the JSON under client_email).

⚠️ Do NOT push this file to GitHub. Add it to .gitignore if it isn’t already.

Configure your Google Sheet:

    Create a Google Sheet named UserDatabase.

    Add the following headers in the first row:

        username | email | password | failed_attempts | lock_until

        Share it with the service account email.

Usage

    Run the Flask application:

python app.py

Open in browser:

    http://127.0.0.1:5000

    Register a new user via the Sign Up page.

    Login with the registered email and password.

        After 4 failed login attempts, the account will be locked for 30 minutes.

Dependencies / Libraries

    Flask: Secure web framework with CSRF protection.

    Werkzeug: Security utilities for Flask.

    bcrypt: Industry-standard password hashing.

    gspread: Google Sheets API for Python.

    google-auth: Official Google authentication library.

    google-auth-oauthlib & google-auth-httplib2: Google API support libraries.

    re: Python regex for input validation.

    datetime: Time and lock management.

Notes

    Replace app.secret_key in app.py with a unique secret key for production.

    Never commit your credentials.json file.

    The system uses Google Sheets as a lightweight database. Each user running this project must create their own Google credentials.
