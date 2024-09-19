from ..utils.db import db
from sqlalchemy.orm import relationship

class Founder(db.Model):
    """Founder model representing a startup founder in the database"""

    # Define table columns
    id = db.Column(db.Integer, primary_key=True)
    startup_id = db.Column(db.Integer, db.ForeignKey('startup.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(100))
    linkedin_url = db.Column(db.String(255))

    # Define relationship with Startup model
    startup = relationship('Startup', back_populates='founders')

    def to_dict(self):
        """
        Convert the Founder object to a dictionary

        Returns:
            dict: Dictionary representation of the Founder
        """
        # Create a dictionary with all column values
        founder_dict = {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

        # Exclude the 'startup' relationship from the dictionary
        founder_dict.pop('startup', None)

        # Return the dictionary
        return founder_dict