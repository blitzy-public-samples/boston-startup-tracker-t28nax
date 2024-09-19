import pandas as pd
import requests
from bs4 import BeautifulSoup
from src.utils.logger import logger
from src.data_collection.api_integrators.crunchbase_integrator import CrunchbaseIntegrator
from src.data_collection.api_integrators.linkedin_integrator import LinkedinIntegrator

class StartupEnricher:
    """
    Class for enriching startup data with additional information from various sources
    """

    def __init__(self):
        self.crunchbase_integrator = CrunchbaseIntegrator()
        self.linkedin_integrator = LinkedinIntegrator()

    def enrich_startup_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Main method to enrich startup data
        """
        # Initialize API integrators
        logger.info("Starting startup data enrichment process")

        # Enrich with Crunchbase data
        crunchbase_df = self.enrich_with_crunchbase(df)

        # Enrich with LinkedIn data
        linkedin_df = self.enrich_with_linkedin(df)

        # Enrich with web scraping data
        web_df = self.enrich_with_web_scraping(df)

        # Merge enriched data with original DataFrame
        enriched_df = self.merge_enriched_data(df, crunchbase_df, linkedin_df, web_df)

        # Handle conflicts and inconsistencies
        enriched_df = self._handle_conflicts(enriched_df)

        logger.info("Startup data enrichment process completed")
        return enriched_df

    def enrich_with_crunchbase(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich startup data with information from Crunchbase
        """
        enriched_data = []
        for _, row in df.iterrows():
            try:
                crunchbase_data = self.crunchbase_integrator.fetch_startup_data(row['name'])
                enriched_data.append({
                    'name': row['name'],
                    'funding_rounds': crunchbase_data.get('funding_rounds'),
                    'total_funding': crunchbase_data.get('total_funding'),
                    'investors': crunchbase_data.get('investors')
                })
            except Exception as e:
                logger.error(f"Error fetching Crunchbase data for {row['name']}: {str(e)}")
                enriched_data.append({'name': row['name']})

        return pd.DataFrame(enriched_data)

    def enrich_with_linkedin(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich startup data with information from LinkedIn
        """
        enriched_data = []
        for _, row in df.iterrows():
            try:
                linkedin_data = self.linkedin_integrator.fetch_company_data(row['name'])
                enriched_data.append({
                    'name': row['name'],
                    'employee_count': linkedin_data.get('employee_count'),
                    'recent_hires': linkedin_data.get('recent_hires'),
                    'company_size': linkedin_data.get('company_size')
                })
            except Exception as e:
                logger.error(f"Error fetching LinkedIn data for {row['name']}: {str(e)}")
                enriched_data.append({'name': row['name']})

        return pd.DataFrame(enriched_data)

    def enrich_with_web_scraping(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich startup data with information from web scraping
        """
        enriched_data = []
        for _, row in df.iterrows():
            try:
                website = row.get('website')
                if website:
                    response = requests.get(website)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract relevant information (example: meta description)
                    description = soup.find('meta', attrs={'name': 'description'})
                    description = description['content'] if description else None

                    enriched_data.append({
                        'name': row['name'],
                        'website_description': description
                    })
                else:
                    enriched_data.append({'name': row['name']})
            except Exception as e:
                logger.error(f"Error scraping website for {row['name']}: {str(e)}")
                enriched_data.append({'name': row['name']})

        return pd.DataFrame(enriched_data)

    def merge_enriched_data(self, original_df: pd.DataFrame, crunchbase_df: pd.DataFrame, 
                            linkedin_df: pd.DataFrame, web_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge enriched data from various sources with the original DataFrame
        """
        merged_df = original_df.merge(crunchbase_df, on='name', how='left')
        merged_df = merged_df.merge(linkedin_df, on='name', how='left')
        merged_df = merged_df.merge(web_df, on='name', how='left')
        
        return merged_df

    def _handle_conflicts(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle conflicts and inconsistencies in the merged data
        """
        # Implement conflict resolution logic here
        # For example, prefer Crunchbase data over LinkedIn data for funding information
        # This is a placeholder and should be expanded based on specific requirements
        return df

# Human tasks:
# TODO: Review and update API integration strategies
# TODO: Implement more advanced conflict resolution logic
# TODO: Add support for additional data sources
# TODO: Implement rate limiting for Crunchbase API calls
# TODO: Add error handling for failed API requests
# TODO: Develop a strategy for handling startups not found in Crunchbase
# TODO: Implement rate limiting for LinkedIn API calls
# TODO: Add error handling for failed API requests
# TODO: Develop a strategy for handling startups not found on LinkedIn
# TODO: Implement robust error handling for web scraping
# TODO: Develop strategies for handling different website structures
# TODO: Add support for scraping additional relevant websites (e.g., news sites)
# TODO: Develop a comprehensive conflict resolution strategy
# TODO: Implement data quality checks for the merged data
# TODO: Add support for preserving the source of each piece of information