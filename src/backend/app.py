from flask import Flask
from flask_cors import CORS
from config import Config
from utils.db import db
from routes.startup import startup_routes
from routes.investor import investor_routes
from routes.job import job_routes
from routes.news import news_routes
from routes.user import user_routes
from routes.auth import auth_routes

app = Flask(__name__)

def create_app():
    # Create Flask application instance
    app = Flask(__name__)

    # Load configuration from Config object
    app.config.from_object(Config)

    # Initialize CORS with the app
    CORS(app)

    # Initialize database with the app
    db.init_app(app)

    # Register blueprint for startup routes
    app.register_blueprint(startup_routes)

    # Register blueprint for investor routes
    app.register_blueprint(investor_routes)

    # Register blueprint for job routes
    app.register_blueprint(job_routes)

    # Register blueprint for news routes
    app.register_blueprint(news_routes)

    # Register blueprint for user routes
    app.register_blueprint(user_routes)

    # Register blueprint for auth routes
    app.register_blueprint(auth_routes)

    # Return the configured app
    return app

def main():
    # Call create_app to get the Flask application
    app = create_app()

    # Run the application in debug mode if __name__ is '__main__'
    if __name__ == '__main__':
        app.run(debug=True)

main()