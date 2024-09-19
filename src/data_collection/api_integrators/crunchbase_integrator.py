import requests
import json
from datetime import datetime
from ...backend.models.startup import Startup
from ...backend.models.investor import Investor
from ...backend.models.funding_round import FundingRound
from ...backend.utils.db import db
from ...utils.logger import logger

API_BASE_URL: str = "https://api.crunchbase.com/v3.1"
API_KEY: str = "your_crunchbase_api_key_here"

class CrunchbaseIntegrator:
    """Integrator class for collecting data from the Crunchbase API"""

    def fetch_startup_data(self, startup_name: str) -> dict:
        """Fetch startup data from Crunchbase API"""
        # Construct the API endpoint URL
        endpoint = f"{API_BASE_URL}/organizations/{startup_name}"
        
        # Send a GET request to the Crunchbase API
        response = requests.get(endpoint, params={"user_key": API_KEY})
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = json.loads(response.text)
            
            # Extract and return the relevant startup data
            return data.get("data", {}).get("properties", {})
        else:
            logger.error(f"Failed to fetch startup data for {startup_name}")
            return {}

    def fetch_investor_data(self, investor_name: str) -> dict:
        """Fetch investor data from Crunchbase API"""
        # Construct the API endpoint URL
        endpoint = f"{API_BASE_URL}/organizations/{investor_name}"
        
        # Send a GET request to the Crunchbase API
        response = requests.get(endpoint, params={"user_key": API_KEY})
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = json.loads(response.text)
            
            # Extract and return the relevant investor data
            return data.get("data", {}).get("properties", {})
        else:
            logger.error(f"Failed to fetch investor data for {investor_name}")
            return {}

    def fetch_funding_rounds(self, startup_id: str) -> list:
        """Fetch funding round data for a startup from Crunchbase API"""
        # Construct the API endpoint URL
        endpoint = f"{API_BASE_URL}/organizations/{startup_id}/funding_rounds"
        
        # Send a GET request to the Crunchbase API
        response = requests.get(endpoint, params={"user_key": API_KEY})
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = json.loads(response.text)
            
            # Extract and return the relevant funding round data
            return data.get("data", {}).get("items", [])
        else:
            logger.error(f"Failed to fetch funding rounds for startup {startup_id}")
            return []

    def update_startup_data(self, startup_id: int) -> bool:
        """Update startup data in the database with Crunchbase data"""
        # Fetch the startup from the database
        startup = Startup.query.get(startup_id)
        if not startup:
            logger.error(f"Startup with id {startup_id} not found in database")
            return False
        
        # Fetch updated data from Crunchbase API
        crunchbase_data = self.fetch_startup_data(startup.crunchbase_id)
        
        if not crunchbase_data:
            logger.error(f"Failed to fetch Crunchbase data for startup {startup_id}")
            return False
        
        # Update the startup object with new data
        startup.name = crunchbase_data.get("name", startup.name)
        startup.description = crunchbase_data.get("short_description", startup.description)
        startup.founded_date = datetime.strptime(crunchbase_data.get("founded_on", ""), "%Y-%m-%d").date() if crunchbase_data.get("founded_on") else startup.founded_date
        startup.website = crunchbase_data.get("homepage_url", startup.website)
        startup.linkedin_url = crunchbase_data.get("linkedin_url", startup.linkedin_url)
        startup.twitter_url = crunchbase_data.get("twitter_url", startup.twitter_url)
        startup.facebook_url = crunchbase_data.get("facebook_url", startup.facebook_url)
        startup.employee_count = crunchbase_data.get("num_employees_enum", startup.employee_count)
        startup.last_updated = datetime.utcnow()
        
        # Commit changes to the database
        try:
            db.session.commit()
            logger.info(f"Successfully updated startup data for {startup.name}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update startup data for {startup.name}: {str(e)}")
            return False

    def update_investor_data(self, investor_id: int) -> bool:
        """Update investor data in the database with Crunchbase data"""
        # Fetch the investor from the database
        investor = Investor.query.get(investor_id)
        if not investor:
            logger.error(f"Investor with id {investor_id} not found in database")
            return False
        
        # Fetch updated data from Crunchbase API
        crunchbase_data = self.fetch_investor_data(investor.crunchbase_id)
        
        if not crunchbase_data:
            logger.error(f"Failed to fetch Crunchbase data for investor {investor_id}")
            return False
        
        # Update the investor object with new data
        investor.name = crunchbase_data.get("name", investor.name)
        investor.description = crunchbase_data.get("short_description", investor.description)
        investor.website = crunchbase_data.get("homepage_url", investor.website)
        investor.linkedin_url = crunchbase_data.get("linkedin_url", investor.linkedin_url)
        investor.twitter_url = crunchbase_data.get("twitter_url", investor.twitter_url)
        investor.facebook_url = crunchbase_data.get("facebook_url", investor.facebook_url)
        investor.investment_count = crunchbase_data.get("num_investments", investor.investment_count)
        investor.last_updated = datetime.utcnow()
        
        # Commit changes to the database
        try:
            db.session.commit()
            logger.info(f"Successfully updated investor data for {investor.name}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update investor data for {investor.name}: {str(e)}")
            return False

# Human tasks:
# - Implement error handling for API request failures
# - Add rate limiting to comply with Crunchbase API usage limits
# - Implement caching mechanism to reduce API calls for frequently accessed data
# - Implement conflict resolution for data discrepancies
# - Add logging for data updates
# - Implement error handling for database operations
# - Implement pagination to fetch all funding rounds if they span multiple pages