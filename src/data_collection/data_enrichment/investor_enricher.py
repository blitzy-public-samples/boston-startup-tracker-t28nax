import pandas as pd
import requests
from bs4 import BeautifulSoup
from src.utils.logger import logger
from src.data_collection.api_integrators.crunchbase_integrator import CrunchbaseIntegrator
from src.data_collection.api_integrators.linkedin_integrator import LinkedinIntegrator

class InvestorEnricher:
    """
    Class for enriching investor data with additional information from various sources
    """

    def __init__(self):
        self.crunchbase_integrator = CrunchbaseIntegrator()
        self.linkedin_integrator = LinkedinIntegrator()

    def enrich_investor_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Main method to enrich investor data
        """
        # Initialize API integrators
        logger.info("Starting investor data enrichment process")

        # Enrich with Crunchbase data
        crunchbase_df = self.enrich_with_crunchbase(df)

        # Enrich with LinkedIn data
        linkedin_df = self.enrich_with_linkedin(df)

        # Enrich with web scraping data
        web_df = self.enrich_with_web_scraping(df)

        # Merge enriched data with original DataFrame
        enriched_df = self.merge_enriched_data(df, crunchbase_df, linkedin_df, web_df)

        # Handle conflicts and inconsistencies
        enriched_df = self._resolve_conflicts(enriched_df)

        logger.info("Investor data enrichment process completed")
        return enriched_df

    def enrich_with_crunchbase(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich investor data with information from Crunchbase
        """
        enriched_data = []
        for _, investor in df.iterrows():
            try:
                crunchbase_data = self.crunchbase_integrator.fetch_investor_data(investor['name'])
                portfolio_companies = crunchbase_data.get('portfolio_companies', [])
                investment_history = crunchbase_data.get('investment_history', [])
                enriched_data.append({
                    'investor_id': investor['id'],
                    'portfolio_companies': portfolio_companies,
                    'investment_history': investment_history
                })
            except Exception as e:
                logger.error(f"Error fetching Crunchbase data for {investor['name']}: {str(e)}")

        return pd.DataFrame(enriched_data)

    def enrich_with_linkedin(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich investor data with information from LinkedIn
        """
        enriched_data = []
        for _, investor in df.iterrows():
            try:
                linkedin_data = self.linkedin_integrator.fetch_investor_data(investor['name'])
                key_personnel = linkedin_data.get('key_personnel', [])
                recent_activities = linkedin_data.get('recent_activities', [])
                enriched_data.append({
                    'investor_id': investor['id'],
                    'key_personnel': key_personnel,
                    'recent_activities': recent_activities
                })
            except Exception as e:
                logger.error(f"Error fetching LinkedIn data for {investor['name']}: {str(e)}")

        return pd.DataFrame(enriched_data)

    def enrich_with_web_scraping(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich investor data with information from web scraping
        """
        enriched_data = []
        for _, investor in df.iterrows():
            try:
                website = investor['website']
                response = requests.get(website)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract relevant information (example implementation)
                investment_focus = soup.find('meta', {'name': 'investment-focus'})['content'] if soup.find('meta', {'name': 'investment-focus'}) else None
                team_members = [member.text for member in soup.find_all('div', class_='team-member')]

                enriched_data.append({
                    'investor_id': investor['id'],
                    'investment_focus': investment_focus,
                    'team_members': team_members
                })
            except Exception as e:
                logger.error(f"Error scraping web data for {investor['name']}: {str(e)}")

        return pd.DataFrame(enriched_data)

    def merge_enriched_data(self, original_df: pd.DataFrame, crunchbase_df: pd.DataFrame, linkedin_df: pd.DataFrame, web_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge enriched data from various sources with the original DataFrame
        """
        # Merge the original DataFrame with Crunchbase enrichments
        merged_df = pd.merge(original_df, crunchbase_df, left_on='id', right_on='investor_id', how='left')

        # Merge the result with LinkedIn enrichments
        merged_df = pd.merge(merged_df, linkedin_df, left_on='id', right_on='investor_id', how='left')

        # Merge the result with web scraping enrichments
        merged_df = pd.merge(merged_df, web_df, left_on='id', right_on='investor_id', how='left')

        # Drop duplicate columns and clean up
        merged_df = merged_df.drop(columns=['investor_id_x', 'investor_id_y'])

        return merged_df

    def _resolve_conflicts(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle any conflicts or inconsistencies in the merged data
        """
        # Implement conflict resolution logic here
        # For example, prioritize certain data sources, use the most recent data, etc.
        return df

# Human tasks:
# TODO: Review and update API integration strategies
# TODO: Implement more advanced conflict resolution logic
# TODO: Add support for additional data sources specific to investors
# TODO: Implement rate limiting for Crunchbase API calls
# TODO: Add error handling for failed API requests
# TODO: Develop a strategy for handling investors not found in Crunchbase
# TODO: Implement rate limiting for LinkedIn API calls
# TODO: Add error handling for failed API requests
# TODO: Develop a strategy for handling investors not found on LinkedIn
# TODO: Implement robust error handling for web scraping
# TODO: Develop strategies for handling different website structures
# TODO: Add support for scraping additional relevant websites (e.g., financial news sites)
# TODO: Develop a comprehensive conflict resolution strategy
# TODO: Implement data quality checks for the merged data
# TODO: Add support for preserving the source of each piece of information