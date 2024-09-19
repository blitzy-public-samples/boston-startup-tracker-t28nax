# Initialization file for the routes package in the Boston Startup Tracker backend

# Import route modules
from .startup import startup_routes
from .investor import investor_routes
from .job import job_routes
from .news import news_routes
from .user import user_routes
from .auth import auth_routes

# Export route modules for use in other parts of the application
__all__ = [
    'startup_routes',
    'investor_routes',
    'job_routes',
    'news_routes',
    'user_routes',
    'auth_routes'
]