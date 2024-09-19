from ..utils import db
from sqlalchemy.orm import relationship
from datetime import datetime

class Startup(db.Model):
    """Startup model representing a startup company in the database"""

    # Define table columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    website = db.Column(db.String(255))
    industry = db.Column(db.String(100))
    sub_sector = db.Column(db.String(100))
    employee_count = db.Column(db.Integer)
    local_employee_count = db.Column(db.Integer)
    headcount_growth_rate = db.Column(db.Float)
    total_funding = db.Column(db.Float)
    last_funding_date = db.Column(db.Date)
    funding_stage = db.Column(db.String(50))
    is_hiring = db.Column(db.Boolean, default=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    # Define relationships
    founders = relationship('Founder', back_populates='startup')
    executives = relationship('Executive', back_populates='startup')
    funding_rounds = relationship('FundingRound', back_populates='startup')
    job_postings = relationship('JobPosting', back_populates='startup')
    news_articles = relationship('NewsArticle', back_populates='startup')

    def to_dict(self):
        """
        Convert the Startup object to a dictionary
        
        Returns:
            dict: Dictionary representation of the Startup
        """
        # Create a dictionary with all column values
        startup_dict = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        
        # Convert date and datetime objects to ISO format strings
        for key, value in startup_dict.items():
            if isinstance(value, (datetime, db.Date)):
                startup_dict[key] = value.isoformat()
        
        # Return the dictionary
        return startup_dict