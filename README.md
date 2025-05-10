# Conference Registration System

A modern web application built with FastAPI for conference registration and event management.

## 📋 Features

- **Authentication & Authorization**
  - User registration and login
  - JWT authentication with cookie storage
  - Protected routes for authorized users
  - Logout with token invalidation

- **Security**
  - Password hashing using bcrypt
  - Password complexity validation (minimum length, special characters, digits)
  - CSRF protection
  - Rate limiting
  - Content Security Policy for XSS protection

- **Profile Management**
  - View and edit personal information
  - Upload and update profile picture
  - Change password with current password verification

- **Password Recovery**
  - Request password reset via email
  - Verification code confirmation
  - New password setup

- **Participant Management**
  - View list of all registered participants
  - Filter and sort participants
  - Detailed information for each participant

- **User Interface**
  - Responsive design based on Bootstrap 5
  - Interactive forms with client-side validation
  - Password visibility toggle
  - User action notifications
  - Bootstrap Icons for enhanced UI

- **Additional Features**
  - Action and error logging
  - Server-side and client-side form validation
  - Error handling with informative messages
  - Custom 404 page

## 🔧 Requirements

- Python 3.8-3.11 (not compatible with Python 3.12 and above)
- Rust (required for pydantic compilation)
- Visual Studio with C++ build tools (for Windows)
- Dependencies listed in requirements.txt

## 💻 Installation

### 1. Clone the repository

```bash
git clone https://github.com/tsybtw/Conference.git
cd conference
```

### 2. Install prerequisites

#### Rust installation
Rust is required for building some Python dependencies like pydantic:

```bash
# Windows
For Windows:
Visit the official Rust website at https://www.rust-lang.org/tools/install 
or https://rustup.rs/ and download the installer.
Run the installer and follow the on-screen instructions.

# macOS/Linux
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

#### Visual Studio with C++ build tools
Some Python packages require C++ compilation. On Windows, you'll need Visual Studio build tools:

1. Download the Visual Studio installer from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run the installer and select "Desktop development with C++"
3. Complete the installation

### 3. Set up Python environment

```bash
# Windows
For Windows:
python -m venv venv
venv\Scripts\activate

# macOS/Linux
For macOS/Linux:
python -m venv venv
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the root directory:
```
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///./conference.db
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USERNAME=your_email@example.com
EMAIL_PASSWORD=your_email_password
EMAIL_FROM=your_email@example.com
```

## 🚀 Running the Application

### 1. Activate your virtual environment

```bash
# Windows
For Windows:
venv\Scripts\activate

# macOS/Linux
For macOS/Linux:
source venv/bin/activate
```

### 2. Start the application

```bash
python run.py
```

### 3. Access the application

Open your browser and navigate to:
```
http://localhost:8000
```

> **Note:** The application will automatically create the database on first run.

## 🔍 After Installation

- The database will be created automatically on first run
- Register at least one user to access the system
- Once logged in, you can view all registered participants and edit your profile
- The JWT token is stored as a cookie and expires after 30 minutes
- For password recovery to work properly, you need to configure SMTP settings in the .env file

## 📚 API Documentation

FastAPI automatically generates API documentation. You can access it at:
```
http://localhost:8000/api/v1/docs
```

## 📁 Project Structure

```
conference_app/
├── app/
│   ├── api/               # API endpoints
│   │   ├── endpoints/
│   │   │   ├── auth.py
│   │   │   └── users.py
│   │   └── api.py
│   ├── core/              # Core functionality
│   │   ├── database.py
│   │   ├── email.py       # Email sending functionality
│   │   ├── logging.py     # Logging configuration
│   │   ├── rate_limit.py  # Rate limiting functionality
│   │   ├── security.py    # Authentication and security
│   │   └── validation.py  # Data validation functions
│   ├── crud/              # Database operations
│   │   └── user.py
│   ├── models/            # SQLAlchemy models
│   │   └── user.py
│   ├── schemas/           # Pydantic schemas
│   │   ├── token.py
│   │   └── user.py
│   ├── static/            # Static assets
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── main.js    # Client-side functionality including password toggle
│   ├── templates/         # HTML templates
│   │   ├── 404.html
│   │   ├── base.html
│   │   ├── forgot_password.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── profile.html
│   │   ├── register.html
│   │   ├── reset_password.html
│   │   ├── users.html
│   │   └── verify_reset_code.html
│   ├── config.py          # App configuration
│   ├── main.py            # FastAPI app
│   └── web.py             # Web routes
├── logs/                  # Log files directory
├── .env                   # Environment variables
├── .gitignore             # Git ignore file
├── conference.db          # SQLite database
├── README.md              # This file
├── requirements.txt       # Python dependencies
└── run.py                 # Application entry point
```

## 📄 License

MIT