"""
WSGI entrypoint for production deployments (Render, Gunicorn, PythonAnywhere).
"""
from app import app
from database import init_db

# Ensure database tables and seed data are initialized on cloud launch
init_db(seed=True)

if __name__ == "__main__":
    app.run()
