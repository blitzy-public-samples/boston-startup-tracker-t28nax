import requests
import json
from datetime import datetime
from src.backend.models.startup import Startup
from src.backend.models.founder import Founder
from src.backend.models.executive import Executive
from src.backend.models.job_posting import JobPosting
from src.backend.utils.db import db
from src.utils.logger import logger

API_BASE_URL: str = "https://api.linkedin.com/v2"
API_KEY: str = "your_linkedin_api_key_here"

class LinkedinIntegrator:
    """Integrator class for collecting data from the LinkedIn API"""

    def fetch_company_data(self, company_name: str) -> dict:
        """Fetch company data from LinkedIn API"""
        # Construct the API endpoint URL
        endpoint = f"{API_BASE_URL}/companies?q=name&name={company_name}"

        # Send a GET request to the LinkedIn API
        response = requests.get(endpoint, headers={"Authorization": f"Bearer {API_KEY}"})

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = json.loads(response.text)

            # Extract and return the relevant company data
            return data.get("elements", [])[0] if data.get("elements") else {}
        else:
            logger.error(f"Failed to fetch company data for {company_name}: {response.status_code}")
            return {}

    def fetch_employee_data(self, company_id: str) -> list:
        """Fetch employee data for a company from LinkedIn API"""
        # Construct the API endpoint URL
        endpoint = f"{API_BASE_URL}/companies/{company_id}/employees"

        # Send a GET request to the LinkedIn API
        response = requests.get(endpoint, headers={"Authorization": f"Bearer {API_KEY}"})

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = json.loads(response.text)

            # Extract and return the relevant employee data
            return data.get("elements", [])
        else:
            logger.error(f"Failed to fetch employee data for company {company_id}: {response.status_code}")
            return []

    def fetch_job_postings(self, company_id: str) -> list:
        """Fetch job posting data for a company from LinkedIn API"""
        # Construct the API endpoint URL
        endpoint = f"{API_BASE_URL}/companies/{company_id}/jobs"

        # Send a GET request to the LinkedIn API
        response = requests.get(endpoint, headers={"Authorization": f"Bearer {API_KEY}"})

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = json.loads(response.text)

            # Extract and return the relevant job posting data
            return data.get("elements", [])
        else:
            logger.error(f"Failed to fetch job postings for company {company_id}: {response.status_code}")
            return []

    def update_startup_data(self, startup_id: int) -> bool:
        """Update startup data in the database with LinkedIn data"""
        try:
            # Fetch the startup from the database
            startup = Startup.query.get(startup_id)
            if not startup:
                logger.error(f"Startup with id {startup_id} not found")
                return False

            # Fetch updated data from LinkedIn API
            company_data = self.fetch_company_data(startup.name)

            # Update the startup object with new data
            startup.linkedin_id = company_data.get("id")
            startup.description = company_data.get("description")
            startup.website = company_data.get("website")
            startup.industry = company_data.get("industry")
            startup.company_size = company_data.get("companySize", {}).get("value")
            startup.founded_year = company_data.get("foundedYear")
            startup.last_updated = datetime.utcnow()

            # Commit changes to the database
            db.session.commit()

            logger.info(f"Successfully updated startup data for {startup.name}")
            return True
        except Exception as e:
            logger.error(f"Error updating startup data: {str(e)}")
            db.session.rollback()
            return False

    def update_employee_data(self, startup_id: int) -> bool:
        """Update founder and executive data in the database with LinkedIn data"""
        try:
            # Fetch the startup from the database
            startup = Startup.query.get(startup_id)
            if not startup:
                logger.error(f"Startup with id {startup_id} not found")
                return False

            # Fetch updated employee data from LinkedIn API
            employee_data = self.fetch_employee_data(startup.linkedin_id)

            for employee in employee_data:
                # Determine if the employee is a founder or executive
                is_founder = "Founder" in employee.get("title", "")
                is_executive = any(title in employee.get("title", "") for title in ["CEO", "CTO", "CFO", "COO"])

                if is_founder:
                    # Update or create founder
                    founder = Founder.query.filter_by(linkedin_id=employee.get("id")).first()
                    if not founder:
                        founder = Founder(startup_id=startup_id)
                    founder.linkedin_id = employee.get("id")
                    founder.name = employee.get("name")
                    founder.title = employee.get("title")
                    db.session.add(founder)
                elif is_executive:
                    # Update or create executive
                    executive = Executive.query.filter_by(linkedin_id=employee.get("id")).first()
                    if not executive:
                        executive = Executive(startup_id=startup_id)
                    executive.linkedin_id = employee.get("id")
                    executive.name = employee.get("name")
                    executive.title = employee.get("title")
                    db.session.add(executive)

            # Commit changes to the database
            db.session.commit()

            logger.info(f"Successfully updated employee data for startup {startup.name}")
            return True
        except Exception as e:
            logger.error(f"Error updating employee data: {str(e)}")
            db.session.rollback()
            return False

    def update_job_postings(self, startup_id: int) -> bool:
        """Update job posting data in the database with LinkedIn data"""
        try:
            # Fetch the startup from the database
            startup = Startup.query.get(startup_id)
            if not startup:
                logger.error(f"Startup with id {startup_id} not found")
                return False

            # Fetch updated job posting data from LinkedIn API
            job_postings = self.fetch_job_postings(startup.linkedin_id)

            # Get existing job postings
            existing_postings = JobPosting.query.filter_by(startup_id=startup_id).all()
            existing_posting_ids = set(posting.linkedin_id for posting in existing_postings)

            for job in job_postings:
                if job.get("id") in existing_posting_ids:
                    # Update existing job posting
                    posting = next(p for p in existing_postings if p.linkedin_id == job.get("id"))
                    posting.title = job.get("title")
                    posting.description = job.get("description")
                    posting.location = job.get("location", {}).get("name")
                    posting.last_updated = datetime.utcnow()
                else:
                    # Add new job posting
                    new_posting = JobPosting(
                        startup_id=startup_id,
                        linkedin_id=job.get("id"),
                        title=job.get("title"),
                        description=job.get("description"),
                        location=job.get("location", {}).get("name"),
                        posted_date=datetime.utcnow(),
                        last_updated=datetime.utcnow()
                    )
                    db.session.add(new_posting)

                existing_posting_ids.discard(job.get("id"))

            # Remove job postings that are no longer active
            for inactive_id in existing_posting_ids:
                inactive_posting = next(p for p in existing_postings if p.linkedin_id == inactive_id)
                db.session.delete(inactive_posting)

            # Commit changes to the database
            db.session.commit()

            logger.info(f"Successfully updated job postings for startup {startup.name}")
            return True
        except Exception as e:
            logger.error(f"Error updating job postings: {str(e)}")
            db.session.rollback()
            return False

# Human tasks:
# TODO: Implement error handling for API request failures
# TODO: Add rate limiting to comply with LinkedIn API usage limits
# TODO: Implement caching mechanism to reduce API calls for frequently accessed data
# TODO: Implement pagination to fetch all employees if they span multiple pages
# TODO: Implement pagination to fetch all job postings if they span multiple pages
# TODO: Implement conflict resolution for data discrepancies
# TODO: Add logging for data updates
# TODO: Implement error handling for database operations
# TODO: Implement logic to differentiate between founders and executives
# TODO: Implement logic to handle updates to existing job postings