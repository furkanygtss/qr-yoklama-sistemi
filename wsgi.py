"""
WSGI entrypoint for production deployments (Render, Gunicorn, PythonAnywhere).
"""
from app import app

if __name__ == "__main__":
    app.run()
