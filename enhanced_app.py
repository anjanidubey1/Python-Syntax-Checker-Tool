"""
Enhanced Python Code Analyzer Flask Application
A robust web service for checking, linting, and formatting Python code.
"""

import os
import logging
import tempfile
import subprocess
from datetime import datetime
from functools import wraps
from typing import Dict, Any, Optional

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge

# Try importing optional libraries
try:
    import flake8
except ImportError:
    flake8 = None

try:
    import black
except ImportError:
    black = None

try:
    import radon.complexity as radon_cc
    import radon.metrics as radon_metrics
except ImportError:
    radon_cc = None
    radon_metrics = None


# Configuration
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    MAX_CONTENT_LENGTH = 1024 * 1024  # 1MB max file size
    RATE_LIMIT_PER_MINUTE = 60
    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"


app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for all routes
CORS(app, origins="*")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Simple rate limiting (in production, use Redis or similar)
request_counts = {}


def rate_limit(max_requests: int = Config.RATE_LIMIT_PER_MINUTE):
    """Simple rate limiting decorator"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.environ.get("HTTP_X_FORWARDED_FOR", request.remote_addr)
            current_minute = datetime.now().strftime("%Y-%m-%d %H:%M")
            key = f"{client_ip}:{current_minute}"

            if key in request_counts:
                request_counts[key] += 1
            else:
                request_counts[key] = 1
                # Clean old entries
                keys_to_remove = [
                    k for k in request_counts.keys() if not k.endswith(current_minute)
                ]
                for k in keys_to_remove:
                    del request_counts[k]

            if request_counts[key] > max_requests:
                logger.warning(f"Rate limit exceeded for {client_ip}")
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": "Rate limit exceeded. Please try again later.",
                        }
                    ),
                    429,
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def validate_code_input(code: str) -> Optional[str]:
    """Validate code input and return error message if invalid"""
    if not code or not isinstance(code, str):
        return "Code input is required and must be a string"

    if len(code.strip()) == 0:
        return "Code input cannot be empty"

    if len(code) > 50000:  # 50KB limit
        return "Code input is too large (max 50KB)"

    # Check for potentially dangerous imports/operations
    dangerous_patterns = [
        "import os",
        "import subprocess",
        "import sys",
        "import shutil",
        "exec(",
        "eval(",
        "__import__",
        "open(",
        "file(",
        "input(",
        "raw_input(",
    ]

    code_lower = code.lower()
    for pattern in dangerous_patterns:
        if pattern in code_lower:
            logger.warning(
                f"Potentially dangerous code pattern detected: {pattern}"
            )
            # Don't block, just log for monitoring

    return None


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return (
        jsonify(
            {"status": "error", "message": "Request too large. Maximum file size is 1MB."}
        ),
        413,
    )


@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {error}")
    return (
        jsonify(
            {
                "status": "error",
                "message": "An internal server error occurred. Please try again later.",
            }
        ),
        500,
    )


@app.route("/")
def index():
    """Renders the main HTML page."""
    return render_template("index.html")


@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "features": {
                "syntax_check": True,
                "linting": flake8 is not None,
                "formatting": black is not None,
                "complexity_analysis": radon_cc is not None,
            },
        }
    )


@app.route("/process_code", methods=["POST"])
@rate_limit()
def process_code():
    """Enhanced code processing endpoint"""
    try:
        if not request.is_json:
            return jsonify({"status": "error", "message": "Request must be JSON"}), 400

        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Invalid JSON data"}), 400

        code = data.get("code", "")
        action = data.get("action", "check")

        # Validate inputs
        validation_error = validate_code_input(code)
        if validation_error:
            return jsonify({"status": "error", "message": validation_error}), 400

        if action not in ["check", "lint", "format", "complexity"]:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Invalid action. Must be one of: check, lint, format, complexity",
                    }
                ),
                400,
            )

        logger.info(f"Processing code with action: {action}")

        if action == "check":
            return handle_syntax_check(code)
        elif action == "lint":
            return handle_linting(code)
        elif action == "format":
            return handle_formatting(code)
        elif action == "complexity":
            return handle_complexity_analysis(code)

    except Exception as e:
        logger.error(f"Error in process_code: {str(e)}", exc_info=True)
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "An unexpected error occurred while processing your code.",
                }
            ),
            500,
        )


def handle_syntax_check(code: str) -> Dict[str, Any]:
    """Handle syntax checking"""
    try:
        compile(code, "<string>", "exec")
        return jsonify(
            {
                "status": "success",
                "message": "Syntax is valid! ✓",
                "details": {"lines": len(code.splitlines()), "characters": len(code)},
            }
        )
    except SyntaxError as e:
        return jsonify(
            {
                "status": "error",
                "message": f"Syntax Error on line {e.lineno}: {e.msg}",
                "details": {
                    "line_number": e.lineno,
                    "column": e.offset,
                    "error_type": "SyntaxError",
                },
            }
        )


def handle_linting(code: str) -> Dict[str, Any]:
    """Handle code linting with flake8"""
    if not flake8:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Linting is not available. The 'flake8' library is not installed.",
                }
            ),
            503,
        )

    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w+", suffix=".py", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(code)
            temp_file = tmp.name

        result = subprocess.run(
            ["flake8", "--ignore=W292,W391,E501,E203", "--max-line-length=88", temp_file],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )

        if not result.stdout.strip():
            return jsonify(
                {
                    "status": "success",
                    "message": "No linting issues found! ✓",
                    "details": {
                        "issues_count": 0,
                        "lines_checked": len(code.splitlines()),
                    },
                }
            )
        else:
            raw_errors = result.stdout.strip().split("\n")
            lint_errors = [
                err.replace(temp_file + ":", "Line ") for err in raw_errors if temp_file in err
            ]

            return jsonify(
                {
                    "status": "lint_errors",
                    "message": f"Found {len(lint_errors)} linting issue(s)",
                    "errors": lint_errors,
                    "details": {
                        "issues_count": len(lint_errors),
                        "lines_checked": len(code.splitlines()),
                    },
                }
            )

    except subprocess.TimeoutExpired:
        return jsonify(
            {
                "status": "error",
                "message": "Linting operation timed out. Code may be too complex.",
            }
        ), 408

    except Exception as e:
        logger.error(f"Error in linting: {str(e)}")
        return jsonify({"status": "error", "message": f"Linting failed: {str(e)}"}), 500

    finally:
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except OSError:
                logger.warning(f"Failed to delete temporary file: {temp_file}")


def handle_formatting(code: str) -> Dict[str, Any]:
    """Handle code formatting with Black"""
    if not black:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Formatting is not available. The 'black' library is not installed.",
                }
            ),
            503,
        )

    try:
        try:
            compile(code, "<string>", "exec")
        except SyntaxError as e:
            return jsonify(
                {
                    "status": "error",
                    "message": f"Cannot format due to syntax error on line {e.lineno}: {e.msg}",
                    "details": {"line_number": e.lineno, "error_type": "SyntaxError"},
                }
            )

        formatted_code = black.format_str(
            code,
            mode=black.FileMode(line_length=88, string_normalization=True, is_pyi=False),
        )

        if formatted_code.strip() == code.strip():
            return jsonify(
                {
                    "status": "success",
                    "message": "Code is already properly formatted! ✓",
                    "formatted_code": formatted_code,
                    "details": {
                        "changed": False,
                        "lines": len(formatted_code.splitlines()),
                    },
                }
            )
        else:
            return jsonify(
                {
                    "status": "success",
                    "message": "Code has been formatted successfully! ✓",
                    "formatted_code": formatted_code,
                    "details": {
                        "changed": True,
                        "original_lines": len(code.splitlines()),
                        "formatted_lines": len(formatted_code.splitlines()),
                    },
                }
            )

    except Exception as e:
        logger.error(f"Error in formatting: {str(e)}")
        return jsonify({"status": "error", "message": f"Formatting failed: {str(e)}"}), 500


def handle_complexity_analysis(code: str) -> Dict[str, Any]:
    """Handle complexity analysis with Radon"""
    if not radon_cc:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Complexity analysis is not available. The 'radon' library is not installed.",
                }
            ),
            503,
        )

    try:
        try:
            compile(code, "<string>", "exec")
        except SyntaxError as e:
            return jsonify(
                {
                    "status": "error",
                    "message": f"Cannot analyze complexity due to syntax error on line {e.lineno}: {e.msg}",
                }
            )

        complexity_results = radon_cc.cc_visit(code)
        metrics_results = radon_metrics.mi_visit(code, multi=True)

        functions = []
        total_complexity = 0

        for result in complexity_results:
            complexity_info = {
                "name": result.name,
                "type": result.__class__.__name__.lower().replace("node", ""),
                "complexity": result.complexity,
                "line": result.lineno,
                "rank": result.letter,
            }
            functions.append(complexity_info)
            total_complexity += result.complexity

        mi_score = metrics_results if isinstance(metrics_results, (int, float)) else 0

        if total_complexity <= 10:
            assessment = "Low complexity - Easy to maintain"
        elif total_complexity <= 20:
            assessment = "Moderate complexity - Generally maintainable"
        elif total_complexity <= 50:
            assessment = "High complexity - Consider refactoring"
        else:
            assessment = "Very high complexity - Refactoring recommended"

        return jsonify(
            {
                "status": "success",
                "message": "Complexity analysis completed! ✓",
                "analysis": {
                    "total_complexity": total_complexity,
                    "maintainability_index": round(mi_score, 2) if mi_score else "N/A",
                    "functions": functions,
                    "assessment": assessment,
                    "recommendations": get_complexity_recommendations(
                        total_complexity, functions
                    ),
                },
                "details": {
                    "functions_analyzed": len(functions),
                    "lines_analyzed": len(code.splitlines()),
                },
            }
        )

    except Exception as e:
        logger.error(f"Error in complexity analysis: {str(e)}")
        return jsonify(
            {"status": "error", "message": f"Complexity analysis failed: {str(e)}"}
        ), 500


def get_complexity_recommendations(total_complexity: int, functions: list) -> list:
    """Generate recommendations based on complexity analysis"""
    recommendations = []

    if total_complexity > 20:
        recommendations.append(
            "Consider breaking down complex functions into smaller ones"
        )

    high_complexity_functions = [f for f in functions if f["complexity"] > 10]
    if high_complexity_functions:
        recommendations.append(
            f"Functions with high complexity: {', '.join([f['name'] for f in high_complexity_functions])}"
        )

    if len(functions) > 10:
        recommendations.append("Consider organizing code into classes or modules")

    if not recommendations:
        recommendations.append("Code complexity looks good! Keep up the good work.")

    return recommendations


if __name__ == "__main__":
    logger.info("Starting Enhanced Python Code Analyzer")
    app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
