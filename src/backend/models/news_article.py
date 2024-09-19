from ..utils import db
from sqlalchemy.orm import relationship
from datetime import datetime

class NewsArticle(db.Model):
    """NewsArticle model representing a news article related to a startup in the database"""

    # Define table columns
    id = db.Column(db.Integer, primary_key=True)
    startup_id = db.Column(db.Integer, db.ForeignKey('startup.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(512), nullable=False)
    published_date = db.Column(db.DateTime, nullable=False)
    source = db.Column(db.String(100))
    summary = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Define relationship
    startup = relationship('Startup', back_populates='news_articles')

    def to_dict(self):
        """
        Convert the NewsArticle object to a dictionary

        Returns:
            dict: Dictionary representation of the NewsArticle
        """
        # Create a dictionary with all column values
        article_dict = {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

        # Convert datetime objects to ISO format strings
        for key, value in article_dict.items():
            if isinstance(value, datetime):
                article_dict[key] = value.isoformat()

        # Exclude the 'startup' relationship from the dictionary
        article_dict.pop('startup', None)

        # Return the dictionary
        return article_dict