from ..utils.db import db
from sqlalchemy.orm import relationship

class Executive(db.Model):
    """Executive model representing a startup executive in the database"""

    # Define table columns
    id = db.Column(db.Integer, primary_key=True)
    startup_id = db.Column(db.Integer, db.ForeignKey('startup.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(100))
    linkedin_url = db.Column(db.String(255))

    # Define relationship with Startup model
    startup = relationship('Startup', back_populates='executives')

    def to_dict(self):
        """
        Convert the Executive object to a dictionary

        Returns:
            dict: Dictionary representation of the Executive
        """
        # Create a dictionary with all column values
        exec_dict = {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

        # Exclude the 'startup' relationship from the dictionary
        exec_dict.pop('startup', None)

        # Return the dictionary
        return exec_dict