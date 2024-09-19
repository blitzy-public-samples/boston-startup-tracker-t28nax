from ..utils.db import db
from sqlalchemy.orm import relationship
from sqlalchemy import Table

# Define the many-to-many relationship table for funding rounds and investors
funding_round_investors = Table('funding_round_investors', db.Model.metadata,
    db.Column('funding_round_id', db.Integer, db.ForeignKey('funding_round.id')),
    db.Column('investor_id', db.Integer, db.ForeignKey('investor.id'))
)

class FundingRound(db.Model):
    """FundingRound model representing a funding round in the database"""

    # Define table columns
    id = db.Column(db.Integer, primary_key=True)
    startup_id = db.Column(db.Integer, db.ForeignKey('startup.id'), nullable=False)
    amount = db.Column(db.Float)
    date = db.Column(db.Date)
    round_type = db.Column(db.String(50))

    # Define relationships
    startup = relationship('Startup', back_populates='funding_rounds')
    investors = relationship('Investor', secondary=funding_round_investors, back_populates='funding_rounds')

    def to_dict(self):
        """
        Convert the FundingRound object to a dictionary
        
        Returns:
            dict: Dictionary representation of the FundingRound
        """
        # Create a dictionary with all column values
        result = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        
        # Convert date object to ISO format string
        if self.date:
            result['date'] = self.date.isoformat()
        
        # Add a list of investor names to the dictionary
        result['investor_names'] = [investor.name for investor in self.investors]
        
        # Exclude the 'startup' and 'investors' relationships from the dictionary
        result.pop('startup', None)
        result.pop('investors', None)
        
        return result