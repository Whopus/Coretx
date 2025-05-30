# Coretx Test Project

This is a simple test project designed to demonstrate and test the capabilities of Coretx, an advanced code localization engine that uses LLMs to analyze code repositories and locate relevant code sections based on natural language queries.

## Project Structure

```
coretx_test_project/
├── README.md              # This file
├── test_coretx.py         # Main test script for Coretx
├── sample_app.py          # Sample web application with authentication
├── utils.py               # Utility functions and helpers
├── web_server.py          # Simple HTTP server implementation
└── config.py              # Configuration management
```

## Sample Application

The test project includes a sample web application with the following features:

- **User Authentication**: Registration, login, logout functionality
- **Session Management**: Token-based session handling
- **Database Operations**: SQLite database with users and sessions tables
- **Password Security**: Password hashing and validation
- **Input Validation**: Email, username, and password validation
- **Web Server**: Simple HTTP server with REST API endpoints
- **Configuration Management**: Environment-based configuration

## Test Scenarios

The test script (`test_coretx.py`) includes various natural language queries to test Coretx's code localization capabilities:

1. **Authentication Bug**: "There's a bug in the user authentication system where login fails with valid credentials"
2. **Password Security**: "Find code related to password hashing and security vulnerabilities"
3. **Session Management**: "Locate session management code that handles user sessions and tokens"
4. **Database Issues**: "Find database connection and initialization code that might cause connection errors"
5. **Input Validation**: "Locate input validation and sanitization functions for security"
6. **API Endpoints**: "Find the registration API endpoint that returns incorrect error messages"
7. **Configuration**: "Locate configuration management code and settings"
8. **Web Server**: "Find web server code that handles HTTP requests and responses"

## OpenAI Configuration

The test script is configured to use the following OpenAI API settings:

- **API Key**: `sk-Do6..`
- **Base URL**: `https://ai.comfly.chat/v1/`
- **Model**: `gpt-4.1`

## Running the Tests

### Prerequisites

1. Make sure Coretx is installed:
   ```bash
   cd /workspace/Coretx
   pip install -e .
   ```

2. Navigate to the test project directory:
   ```bash
   cd /workspace/coretx_test_project
   ```

### Running the Test Script

Execute the main test script:

```bash
python test_coretx.py
```

The script will present you with three testing options:

1. **Single Comprehensive Test** (recommended): Tests one complex authentication scenario using all three Coretx methods
2. **Multiple Test Scenarios**: Runs 8 different test scenarios covering various aspects of the codebase
3. **Quick Test Only**: Runs a single quick test for basic functionality

### Test Methods

The script tests three different ways to use Coretx:

1. **`quick_localize()`**: The simplest method for quick code localization
2. **`create_locator()`**: More control with custom configuration
3. **Custom `LocAgentConfig`**: Full control over all configuration parameters

## Expected Results

When running the tests, you should see:

- ✅ Successful import of Coretx
- 🔍 Analysis of natural language queries
- 📊 Results showing located files, classes, and functions
- ⏱️ Performance metrics (duration, tokens used, iterations)
- 💾 Results saved to `coretx_test_results.json`

## Sample Output

```
🎉 Welcome to Coretx Testing Suite
==================================================
🔧 Initialized Coretx Tester
📁 Test project path: /workspace/coretx_test_project
🤖 Model: gpt-4.1
🌐 API Base URL: https://ai.comfly.chat/v1/
✅ All test files found: ['sample_app.py', 'utils.py', 'web_server.py', 'config.py']

🎯 Running Single Comprehensive Test
============================================================

🔬 Testing with Quick Localize
🔍 Testing quick_localize with: 'I'm experiencing an issue where users can't log in...'
⏱️  Analysis completed in 15.32 seconds

📊 Results for Quick Localize:
==================================================
✅ Test successful
⏱️  Duration: 15.32 seconds
📁 Files found: 3
   • sample_app.py
   • utils.py
   • config.py
🏗️  Classes found: 4
   • UserManager
   • PasswordManager
   • SessionManager
⚡ Functions found: 8
   • authenticate_user
   • hash_password
   • verify_password
💬 Conversation turns: 6
🎯 Total tokens used: 2847
🔄 Iterations: 3
```

## Understanding the Results

The test results will show:

- **Files**: Python files that contain relevant code
- **Classes**: Class definitions related to the query
- **Functions**: Function definitions that match the problem description
- **Performance Metrics**: Duration, token usage, and iteration count
- **Conversation**: Number of turns in the LLM conversation

## Troubleshooting

If you encounter issues:

1. **Import Error**: Make sure Coretx is properly installed
2. **API Error**: Verify the OpenAI API key and base URL are correct
3. **Network Error**: Check internet connectivity to the API endpoint
4. **Rate Limiting**: Add delays between tests if you hit rate limits

## Files Description

### `sample_app.py`
A complete web application with:
- Database management (SQLite)
- User registration and authentication
- Session management with tokens
- Password hashing and verification
- API request handling

### `utils.py`
Utility functions including:
- Input validation and sanitization
- Email and username validation
- Password strength calculation
- Configuration management
- Logging setup

### `web_server.py`
HTTP server implementation with:
- REST API endpoints
- Request routing and handling
- CORS support
- Error handling
- HTML frontend for testing

### `config.py`
Configuration management with:
- Environment-based settings
- Development/production configs
- Security settings
- Validation rules
- Error/success messages

## Next Steps

After running the tests, you can:

1. Examine the `coretx_test_results.json` file for detailed results
2. Modify the natural language queries to test different scenarios
3. Add more complex code to the sample application
4. Experiment with different Coretx configuration parameters
5. Test with different OpenAI models or endpoints

This test project demonstrates Coretx's ability to understand natural language descriptions of code issues and accurately locate relevant code sections across multiple files and programming constructs.
