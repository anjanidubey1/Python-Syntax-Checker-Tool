# Python Code Studio Pro

An advanced, professional-grade web application for Python code analysis, formatting, and quality assessment. Built with Flask and featuring a modern, responsive user interface.

## 🚀 Features

### Core Functionality
- **Syntax Checking**: Validate Python code syntax with detailed error reporting
- **Code Linting**: Advanced linting using flake8 with customizable rules
- **Code Formatting**: Automatic code formatting using Black formatter
- **Complexity Analysis**: Code complexity analysis using Radon metrics

### Advanced Features
- **Real-time Statistics**: Live line count, character count, and file information
- **File Management**: Upload Python files, download formatted code
- **Theme Support**: Dark/light theme toggle with multiple editor themes
- **Settings Panel**: Customizable editor preferences and application settings
- **Toast Notifications**: User-friendly feedback system
- **Health Monitoring**: System health check endpoint
- **Share Functionality**: Code sharing capabilities (extensible)

### Security & Performance
- **CORS Support**: Cross-origin request handling
- **Rate Limiting**: Built-in request rate limiting
- **Input Validation**: Comprehensive code input validation
- **Error Handling**: Robust error handling with detailed logging
- **Resource Management**: Automatic cleanup of temporary files

## 🛠 Installation

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Quick Setup

1. **Clone or download the application files**
2. **Install dependencies**:
   ```bash
   pip install -r enhanced_requirements.txt
   ```

3. **Run the application**:
   ```bash
   python enhanced_app.py
   ```

4. **Access the application**:
   Open your browser and navigate to `http://localhost:5000`

### Dependencies

The application requires the following Python packages:
- Flask>=2.3.0
- Flask-CORS>=4.0.0
- black>=23.0.0
- flake8>=6.0.0
- radon>=6.0.0
- Werkzeug>=2.3.0

## 📁 Project Structure

```
python-code-studio-pro/
├── enhanced_app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html              # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css           # Application styles
│   └── js/
│       └── app.js              # Frontend JavaScript
├── README.md                   # This file
├── test_results.md             # Testing documentation
└── app.log                     # Application logs (created at runtime)
```

## 🎯 Usage

### Basic Operations

1. **Syntax Check**: 
   - Select the "Syntax Check" tab
   - Click "Run Syntax Check" to validate your Python code

2. **Code Linting**:
   - Select the "Linter" tab
   - Click "Run Linter" to identify code quality issues

3. **Code Formatting**:
   - Select the "Formatter" tab
   - Click "Run Formatter" to automatically format your code

4. **Complexity Analysis**:
   - Select the "Complexity" tab
   - Click "Run Complexity" to analyze code complexity metrics

### File Operations

- **Upload File**: Click "Upload File" to load a Python file into the editor
- **Download Code**: Click "Download Code" to save your code as a .py file
- **Copy Code**: Use the copy button in the editor header
- **Clear Editor**: Use the trash button to clear the editor content

### Customization

- **Theme Toggle**: Click the moon/sun icon to switch between dark and light themes
- **Settings**: Click the gear icon to access editor preferences
- **Editor Themes**: Choose from Dracula, Default, Monokai, and Material themes
- **Font Size**: Adjust editor font size from 12px to 24px
- **Line Wrapping**: Enable/disable line wrapping in the editor

## 🔧 Configuration

### Environment Variables

- `FLASK_DEBUG`: Set to 'true' for debug mode (default: false)
- `SECRET_KEY`: Flask secret key (default: development key)

### Application Settings

The application includes several configurable settings:

- **Max Content Length**: 1MB file size limit
- **Rate Limit**: 60 requests per minute per IP
- **Flake8 Rules**: Customizable linting rules
- **Black Formatting**: Configurable formatting options

## 🏥 Health Check

The application includes a health check endpoint at `/health` that returns:

```json
{
  "status": "healthy",
  "timestamp": "2025-08-06T09:41:31.725361",
  "features": {
    "complexity_analysis": true,
    "formatting": true,
    "linting": true,
    "syntax_check": true
  }
}
```

## 🚀 Deployment

### Local Development
```bash
python enhanced_app.py
```

### Production Deployment
For production deployment, consider:

1. **Use a WSGI server** (e.g., Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 enhanced_app:app
   ```

2. **Set environment variables**:
   ```bash
   export FLASK_DEBUG=false
   export SECRET_KEY=your-secret-key-here
   ```

3. **Configure reverse proxy** (e.g., Nginx) for static files and SSL

## 🧪 Testing

The application has been thoroughly tested with all features working correctly:

- ✅ Syntax checking with detailed error reporting
- ✅ Linting with flake8 integration
- ✅ Code formatting with Black
- ✅ Complexity analysis with Radon
- ✅ File upload/download functionality
- ✅ Theme switching and settings
- ✅ Health check endpoint
- ✅ Error handling and validation
- ✅ Responsive design and mobile support

See `test_results.md` for detailed testing documentation.

## 🔒 Security Features

- **Input Validation**: Comprehensive validation of code input
- **Rate Limiting**: Protection against abuse
- **CORS Configuration**: Secure cross-origin request handling
- **Error Handling**: Secure error messages without information leakage
- **File Size Limits**: Protection against large file uploads
- **Dangerous Pattern Detection**: Monitoring for potentially harmful code patterns

## 🎨 UI/UX Features

- **Modern Design**: Professional dark theme with light theme option
- **Responsive Layout**: Works on desktop, tablet, and mobile devices
- **Code Editor**: Syntax-highlighted editor with multiple themes
- **Real-time Feedback**: Live statistics and toast notifications
- **Keyboard Shortcuts**: Efficient keyboard navigation
- **Loading States**: Visual feedback during processing
- **Modal Dialogs**: Settings and sharing functionality

## 📝 API Endpoints

- `GET /`: Main application interface
- `POST /process_code`: Code processing endpoint
- `GET /health`: System health check

### Process Code API

**Endpoint**: `POST /process_code`

**Request Body**:
```json
{
  "code": "Python code string",
  "action": "check|lint|format|complexity"
}
```

**Response Examples**:

Syntax Check Success:
```json
{
  "status": "success",
  "message": "Syntax is valid! ✓",
  "details": {
    "lines": 47,
    "characters": 1162
  }
}
```

Linting Issues:
```json
{
  "status": "lint_errors",
  "message": "Found 3 linting issue(s)",
  "errors": ["Line 1:1: F401 'os' imported but unused"],
  "details": {
    "issues_count": 3,
    "lines_checked": 47
  }
}
```

## 🤝 Contributing

This application was developed as an enhanced version of a Python code analysis tool. Future enhancements could include:

- Integration with additional linting tools (pylint, mypy)
- Code coverage analysis
- Git integration for version control
- Plugin system for custom analyzers
- Collaborative editing features
- Cloud storage integration

## 📄 License

This project is developed for educational and professional use. Please ensure compliance with all dependency licenses.

## 👨‍💻 Developer

**Developed & Maintained with ❤️ by Anjani Dubey**

---

## 🚀 Quick Start Guide

1. **Install dependencies**: `pip install -r enhanced_requirements.txt`
2. **Run the application**: `python enhanced_app.py`
3. **Open browser**: Navigate to `http://localhost:5000`
4. **Start coding**: Paste your Python code and select an analysis tool
5. **Enjoy**: Professional code analysis at your fingertips!

For support or questions, please refer to the test results and documentation provided.

