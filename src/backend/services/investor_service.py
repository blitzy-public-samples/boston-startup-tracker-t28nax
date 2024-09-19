from src.backend.utils import db
from src.backend.models.investor import Investor
from src.backend.models.funding_round import FundingRound
import sqlalchemy

def get_investors(filters: dict, page: int, per_page: int) -> tuple:
    # Create a base query for Investor model
    query = db.session.query(Investor)

    # Apply filters to the query if provided
    if filters:
        for key, value in filters.items():
            query = query.filter(getattr(Investor, key) == value)

    # Calculate total count of matching investors
    total_count = query.count()

    # Apply pagination to the query
    query = query.offset((page - 1) * per_page).limit(per_page)

    # Execute the query and return results along with total count
    return query.all(), total_count

# Human tasks:
# - Implement more advanced filtering options (e.g., by investment stage, industry focus)
# - Add sorting functionality (e.g., by total investments, number of portfolio companies)
# - Optimize query performance for large datasets

def get_investor_by_id(investor_id: int) -> Investor:
    # Query the database for an Investor with the given ID
    investor = db.session.query(Investor).get(investor_id)

    # Return the Investor object if found, otherwise return None
    return investor

# Human tasks:
# - Add caching mechanism for frequently accessed investors

def create_investor(investor_data: dict) -> Investor:
    # Create a new Investor object with the provided data
    new_investor = Investor(**investor_data)

    # Add the new Investor to the database session
    db.session.add(new_investor)

    # Commit the changes to the database
    db.session.commit()

    # Return the created Investor object
    return new_investor

# Human tasks:
# - Implement data validation for investor creation
# - Add support for creating related entities (e.g., investment history) in the same transaction

def update_investor(investor_id: int, investor_data: dict) -> Investor:
    # Query the database for the Investor with the given ID
    investor = db.session.query(Investor).get(investor_id)

    # If not found, raise an exception
    if not investor:
        raise ValueError(f"Investor with id {investor_id} not found")

    # Update the Investor object with the provided data
    for key, value in investor_data.items():
        setattr(investor, key, value)

    # Commit the changes to the database
    db.session.commit()

    # Return the updated Investor object
    return investor

# Human tasks:
# - Implement partial update functionality
# - Add validation to prevent updates to read-only fields

def delete_investor(investor_id: int) -> bool:
    # Query the database for the Investor with the given ID
    investor = db.session.query(Investor).get(investor_id)

    # If found, delete the Investor from the database
    if investor:
        db.session.delete(investor)
        db.session.commit()
        return True

    # Return False if not found
    return False

# Human tasks:
# - Implement soft delete functionality
# - Add cascading delete for related entities (e.g., investment history)

def get_investor_portfolio(investor_id: int) -> list:
    # Query the database for FundingRound objects associated with the given investor_id
    funding_rounds = db.session.query(FundingRound).filter(FundingRound.investor_id == investor_id).all()

    # Extract unique startups from the funding rounds
    startups = list(set(fr.startup for fr in funding_rounds))

    # Return the list of Startup objects
    return startups

# Human tasks:
# - Add pagination support for investors with large portfolios
# - Implement sorting options (e.g., by investment date, amount invested)
# - Add filtering options (e.g., by startup stage, industry)

def get_investor_investment_history(investor_id: int) -> list:
    # Query the database for FundingRound objects associated with the given investor_id
    funding_rounds = db.session.query(FundingRound).filter(FundingRound.investor_id == investor_id).all()

    # Return the list of FundingRound objects
    return funding_rounds

# Human tasks:
# - Add pagination support for investors with many investments
# - Implement sorting options (e.g., by date, amount)
# - Add aggregation functionality (e.g., total invested, average investment size)