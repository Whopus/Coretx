"""
Simple web server for the sample application.
"""

import json
import socket
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any

from sample_app import APIHandler
from utils import setup_logging, generate_response, parse_json_safely


class WebRequestHandler(BaseHTTPRequestHandler):
    """Handles HTTP requests for the web application."""
    
    def __init__(self, *args, **kwargs):
        self.api_handler = APIHandler()
        self.logger = setup_logging()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path == '/':
            self.serve_homepage()
        elif path == '/health':
            self.serve_health_check()
        elif path == '/api/profile':
            self.handle_profile_request()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            request_data = parse_json_safely(post_data) or {}
        except Exception:
            self.send_json_response(400, {"error": "Invalid JSON"})
            return
        
        if path == '/api/register':
            self.handle_register_request(request_data)
        elif path == '/api/login':
            self.handle_login_request(request_data)
        elif path == '/api/logout':
            self.handle_logout_request(request_data)
        else:
            self.send_error(404, "Not Found")
    
    def serve_homepage(self):
        """Serve the homepage."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sample App</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 600px; margin: 0 auto; }
                .form-group { margin: 15px 0; }
                input, button { padding: 10px; margin: 5px; }
                button { background: #007cba; color: white; border: none; cursor: pointer; }
                .response { margin: 20px 0; padding: 10px; background: #f0f0f0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Sample Application</h1>
                
                <h2>Register</h2>
                <div class="form-group">
                    <input type="text" id="reg-username" placeholder="Username">
                    <input type="email" id="reg-email" placeholder="Email">
                    <input type="password" id="reg-password" placeholder="Password">
                    <button onclick="register()">Register</button>
                </div>
                
                <h2>Login</h2>
                <div class="form-group">
                    <input type="text" id="login-username" placeholder="Username">
                    <input type="password" id="login-password" placeholder="Password">
                    <button onclick="login()">Login</button>
                </div>
                
                <div class="form-group">
                    <button onclick="getProfile()">Get Profile</button>
                    <button onclick="logout()">Logout</button>
                </div>
                
                <div id="response" class="response"></div>
            </div>
            
            <script>
                let sessionToken = '';
                
                async function register() {
                    const data = {
                        username: document.getElementById('reg-username').value,
                        email: document.getElementById('reg-email').value,
                        password: document.getElementById('reg-password').value
                    };
                    
                    const response = await fetch('/api/register', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    document.getElementById('response').innerHTML = JSON.stringify(result, null, 2);
                }
                
                async function login() {
                    const data = {
                        username: document.getElementById('login-username').value,
                        password: document.getElementById('login-password').value
                    };
                    
                    const response = await fetch('/api/login', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    if (result.success) {
                        sessionToken = result.session_token;
                    }
                    document.getElementById('response').innerHTML = JSON.stringify(result, null, 2);
                }
                
                async function getProfile() {
                    const response = await fetch('/api/profile?session_token=' + sessionToken);
                    const result = await response.json();
                    document.getElementById('response').innerHTML = JSON.stringify(result, null, 2);
                }
                
                async function logout() {
                    const response = await fetch('/api/logout', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({session_token: sessionToken})
                    });
                    
                    const result = await response.json();
                    sessionToken = '';
                    document.getElementById('response').innerHTML = JSON.stringify(result, null, 2);
                }
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def serve_health_check(self):
        """Serve health check endpoint."""
        response = {
            "status": "healthy",
            "service": "sample-app",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        self.send_json_response(200, response)
    
    def handle_register_request(self, request_data: Dict):
        """Handle user registration."""
        try:
            result = self.api_handler.handle_register(request_data)
            status_code = 200 if result.get("success") else 400
            self.send_json_response(status_code, result)
        except Exception as e:
            self.logger.error(f"Registration error: {e}")
            self.send_json_response(500, {"error": "Internal server error"})
    
    def handle_login_request(self, request_data: Dict):
        """Handle user login."""
        try:
            result = self.api_handler.handle_login(request_data)
            status_code = 200 if result.get("success") else 401
            self.send_json_response(status_code, result)
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            self.send_json_response(500, {"error": "Internal server error"})
    
    def handle_profile_request(self):
        """Handle profile retrieval."""
        try:
            # Get session token from query parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            session_token = query_params.get('session_token', [''])[0]
            
            if not session_token:
                self.send_json_response(400, {"error": "Session token required"})
                return
            
            result = self.api_handler.handle_profile(session_token)
            status_code = 200 if result.get("success") else 401
            self.send_json_response(status_code, result)
        except Exception as e:
            self.logger.error(f"Profile error: {e}")
            self.send_json_response(500, {"error": "Internal server error"})
    
    def handle_logout_request(self, request_data: Dict):
        """Handle user logout."""
        try:
            session_token = request_data.get('session_token', '')
            if not session_token:
                self.send_json_response(400, {"error": "Session token required"})
                return
            
            result = self.api_handler.handle_logout(session_token)
            self.send_json_response(200, result)
        except Exception as e:
            self.logger.error(f"Logout error: {e}")
            self.send_json_response(500, {"error": "Internal server error"})
    
    def send_json_response(self, status_code: int, data: Dict):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        json_data = json.dumps(data, indent=2)
        self.wfile.write(json_data.encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Override to use our logger."""
        self.logger.info(f"{self.address_string()} - {format % args}")


class WebServer:
    """Web server wrapper class."""
    
    def __init__(self, host: str = 'localhost', port: int = 8000):
        self.host = host
        self.port = port
        self.server = None
        self.logger = setup_logging()
    
    def start(self):
        """Start the web server."""
        try:
            self.server = HTTPServer((self.host, self.port), WebRequestHandler)
            self.logger.info(f"Starting server on {self.host}:{self.port}")
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.logger.info("Server interrupted by user")
            self.stop()
        except Exception as e:
            self.logger.error(f"Server error: {e}")
    
    def stop(self):
        """Stop the web server."""
        if self.server:
            self.server.shutdown()
            self.logger.info("Server stopped")
    
    def start_in_thread(self):
        """Start server in a separate thread."""
        server_thread = threading.Thread(target=self.start)
        server_thread.daemon = True
        server_thread.start()
        return server_thread


def find_free_port(start_port: int = 8000) -> int:
    """Find a free port starting from the given port."""
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise RuntimeError("No free ports available")


if __name__ == "__main__":
    # Find a free port and start the server
    port = find_free_port()
    server = WebServer(host='0.0.0.0', port=port)
    
    print(f"Starting web server on port {port}")
    print(f"Visit http://localhost:{port} to test the application")
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()