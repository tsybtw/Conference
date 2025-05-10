# Conference Registration System

A web application built with FastAPI for conference registration and participant management.

## 📋 Features

- User registration and authentication
- Secure password storage with bcrypt
- JWT-based authentication
- Responsive UI using Bootstrap 5
- Form validation (both client and server-side)
- List of registered participants (for authenticated users)
- Profile editing

## 🔧 Requirements

- Python 3.8+
- Rust (required for pydantic)
- Visual Studio with C++ build tools (required for some Python dependencies)
- Dependencies listed in requirements.txt

## 💻 Installation

### 1. Clone the repository

```bash
git https://github.com/tsybtw/Conference.git
cd conference
```

### 2. Install prerequisites

#### Rust installation
Rust is required for building some Python dependencies like pydantic:

```bash
# Windows
# Download and run the installer from the official Rust website:
# https://www.rust-lang.org/tools/install
# or
# https://rustup.rs/

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
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment (optional)

Create a `.env` file in the root directory:
```
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///./conference.db
```

## 🚀 Running the Application

### 1. Activate your virtual environment

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
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
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── profile.html
│   │   ├── register.html
│   │   └── users.html
│   ├── config.py          # App configuration
│   ├── main.py            # FastAPI app
│   └── web.py             # Web routes
├── .env                   # Environment variables
├── README.md              # This file
├── requirements.txt       # Python dependencies
└── run.py                 # Application entry point
```

## 📄 License

MIT