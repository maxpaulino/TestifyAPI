
# Imports

from flask import Flask
from flask_cors import CORS
from src.settings import PORT, app
from src.routes import *

# Flask application initialization

CORS(app, origins=[f"http://localhost:{PORT}", "https://chat.openai.com"])

# Main function

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
