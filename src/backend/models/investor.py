# Import necessary modules
from ..utils.db import db
from sqlalchemy.orm import relationship

class Investor(db.Model):
    """Investor model representing an investor in the database"""

    # Define table columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50))
    website = db.Column(db.String(255))

    # Define relationship with FundingRound model
    funding_rounds = relationship('FundingRound', back_populates='investors')

    def to_dict(self):
        """
        Convert the Investor object to a dictionary

        Returns:
            dict: Dictionary representation of the Investor
        """
        # Create a dictionary with all column values
        investor_dict = {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

        # Exclude the 'funding_rounds' relationship from the dictionary
        investor_dict.pop('funding_rounds', None)

        # Return the dictionary
        return investor_dict