from ..utils.db import db
from sqlalchemy.orm import relationship
from datetime import datetime

class JobPosting(db.Model):
    """JobPosting model representing a job posting in the database"""

    # Define table columns
    id = db.Column(db.Integer, primary_key=True)
    startup_id = db.Column(db.Integer, db.ForeignKey('startup.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(100))
    description = db.Column(db.Text)
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Define relationship
    startup = relationship('Startup', back_populates='job_postings')

    def to_dict(self):
        """
        Convert the JobPosting object to a dictionary

        Returns:
            dict: Dictionary representation of the JobPosting
        """
        # Create a dictionary with all column values
        job_dict = {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

        # Convert datetime object to ISO format string
        job_dict['posted_date'] = job_dict['posted_date'].isoformat() if job_dict['posted_date'] else None

        # Exclude the 'startup' relationship from the dictionary
        job_dict.pop('startup', None)

        # Return the dictionary
        return job_dict