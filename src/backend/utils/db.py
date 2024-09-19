from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

def init_db(app):
    """
    Initialize the database with the Flask app
    
    :param app: Flask application instance
    :return: None
    """
    # Initialize the SQLAlchemy instance with the Flask app
    db.init_app(app)
    
    # Create all database tables based on the defined models
    with app.app_context():
        db.create_all()

def get_or_create(model, **kwargs):
    """
    Get an existing database record or create a new one if it doesn't exist
    
    :param model: SQLAlchemy Model
    :param kwargs: Dictionary of key-value pairs to query or create the record
    :return: Tuple of (model instance, boolean indicating if created)
    """
    # Query the database for an existing record matching the provided kwargs
    instance = model.query.filter_by(**kwargs).first()
    
    if instance:
        # If found, return the existing record and False
        return instance, False
    else:
        # If not found, create a new record with the provided kwargs
        instance = model(**kwargs)
        
        # Add the new record to the database session and commit
        db.session.add(instance)
        db.session.commit()
        
        # Return the new record and True
        return instance, True

# Human tasks:
# TODO: Implement database migration strategy using Flask-Migrate
# TODO: Add error handling for database initialization failures
# TODO: Implement a mechanism to check and upgrade the database schema on application startup
# TODO: Add error handling for database query and creation failures
# TODO: Implement a mechanism to handle unique constraint violations
# TODO: Add logging for record creation events