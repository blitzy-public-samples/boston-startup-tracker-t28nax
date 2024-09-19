from src.backend.utils import db
from src.backend.models.user import User
import sqlalchemy
from werkzeug.security import generate_password_hash, check_password_hash

def get_users(filters=None, page=1, per_page=20):
    # Create a base query for User model
    query = User.query

    # Apply filters to the query if provided
    if filters:
        for key, value in filters.items():
            if hasattr(User, key):
                query = query.filter(getattr(User, key) == value)

    # Calculate total count of matching users
    total_count = query.count()

    # Apply pagination to the query
    query = query.offset((page - 1) * per_page).limit(per_page)

    # Execute the query and return results along with total count
    return query.all(), total_count

def get_user_by_id(user_id):
    # Query the database for a User with the given ID
    return User.query.get(user_id)

def get_user_by_email(email):
    # Query the database for a User with the given email
    return User.query.filter_by(email=email).first()

def create_user(user_data):
    # Validate required fields in user_data
    required_fields = ['email', 'password', 'name']
    for field in required_fields:
        if field not in user_data:
            raise ValueError(f"Missing required field: {field}")

    # Check if a user with the given email already exists
    existing_user = get_user_by_email(user_data['email'])
    if existing_user:
        raise ValueError("User with this email already exists")

    # Hash the provided password
    hashed_password = generate_password_hash(user_data['password'])

    # Create a new User object with the provided data and hashed password
    new_user = User(
        email=user_data['email'],
        password=hashed_password,
        name=user_data['name']
    )

    # Add the new User to the database session
    db.session.add(new_user)

    # Commit the changes to the database
    db.session.commit()

    # Return the created User object
    return new_user

def update_user(user_id, user_data):
    # Query the database for the User with the given ID
    user = get_user_by_id(user_id)

    # If not found, raise an exception
    if not user:
        raise ValueError("User not found")

    # Update the User object with the provided data
    for key, value in user_data.items():
        if hasattr(user, key):
            if key == 'password':
                # If password is being updated, hash the new password
                setattr(user, key, generate_password_hash(value))
            else:
                setattr(user, key, value)

    # Commit the changes to the database
    db.session.commit()

    # Return the updated User object
    return user

def delete_user(user_id):
    # Query the database for the User with the given ID
    user = get_user_by_id(user_id)

    # If found, delete the User from the database
    if user:
        db.session.delete(user)
        db.session.commit()
        return True
    
    # Return False if not found
    return False

def authenticate_user(email, password):
    # Query the database for a User with the given email
    user = get_user_by_email(email)

    # If user not found, return None
    if not user:
        return None

    # Check if the provided password matches the stored hash
    if check_password_hash(user.password, password):
        # If password is correct, return the User object
        return user
    
    # If password is incorrect, return None
    return None

# Human tasks:
# - Implement more advanced filtering options (e.g., by role, registration date)
# - Add sorting functionality
# - Optimize query performance for large datasets
# - Add caching mechanism for frequently accessed users
# - Implement case-insensitive email lookup
# - Implement more robust input validation (e.g., password strength, email format)
# - Add email verification process
# - Implement rate limiting to prevent abuse
# - Implement partial update functionality
# - Add validation to prevent updates to read-only fields (e.g., email)
# - Implement access control to allow users to update only their own profile or admin access
# - Implement soft delete functionality to maintain historical data
# - Add authorization check to ensure only admin users can delete other users
# - Implement a process for users to delete their own accounts
# - Implement rate limiting for failed login attempts
# - Add logging for failed login attempts
# - Implement account lockout after multiple failed attempts