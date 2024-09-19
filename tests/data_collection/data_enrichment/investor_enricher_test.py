import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.data_collection.data_enrichment.investor_enricher import InvestorEnricher
from src.data_collection.api_integrators.crunchbase_integrator import CrunchbaseIntegrator
from src.data_collection.api_integrators.linkedin_integrator import LinkedinIntegrator

class TestInvestorEnricher:

    @pytest.fixture
    def sample_investor_data(self):
        return pd.DataFrame({
            'investor_name': ['Acme Ventures', 'Beta Capital'],
            'location': ['Boston, MA', 'Cambridge, MA']
        })

    @pytest.fixture
    def sample_crunchbase_data(self):
        return {
            'Acme Ventures': {'total_investments': 50, 'founded_year': 2005},
            'Beta Capital': {'total_investments': 30, 'founded_year': 2010}
        }

    @pytest.fixture
    def sample_linkedin_data(self):
        return {
            'Acme Ventures': {'employees': 100, 'industry': 'Venture Capital'},
            'Beta Capital': {'employees': 50, 'industry': 'Private Equity'}
        }

    @pytest.fixture
    def sample_html_content(self):
        return """
        <html>
            <body>
                <div class="investor-description">
                    Acme Ventures is a leading VC firm in Boston.
                </div>
            </body>
        </html>
        """

    @pytest.fixture
    def sample_portfolio_companies_data(self):
        return {
            'Acme Ventures': [
                {'name': 'TechCo', 'industry': 'Software'},
                {'name': 'BioMed', 'industry': 'Healthcare'}
            ],
            'Beta Capital': [
                {'name': 'FinTech', 'industry': 'Finance'},
                {'name': 'GreenEnergy', 'industry': 'Renewable Energy'}
            ]
        }

    @patch.object(CrunchbaseIntegrator, 'fetch_investor_data')
    @patch.object(LinkedinIntegrator, 'fetch_company_data')
    def test_enrich_investor_data(self, mock_linkedin, mock_crunchbase, sample_investor_data, sample_crunchbase_data, sample_linkedin_data):
        # Mock the Crunchbase and LinkedIn integrators
        mock_crunchbase.return_value = sample_crunchbase_data
        mock_linkedin.return_value = sample_linkedin_data

        # Create an InvestorEnricher instance
        enricher = InvestorEnricher()

        # Call the enrich_investor_data method
        enriched_data = enricher.enrich_investor_data(sample_investor_data)

        # Assert that the returned DataFrame has the expected enriched data
        assert 'total_investments' in enriched_data.columns
        assert 'employees' in enriched_data.columns
        assert enriched_data.loc[0, 'total_investments'] == 50
        assert enriched_data.loc[1, 'employees'] == 50

    @patch.object(CrunchbaseIntegrator, 'fetch_investor_data')
    def test_enrich_with_crunchbase(self, mock_crunchbase, sample_investor_data, sample_crunchbase_data):
        # Mock the Crunchbase integrator's fetch_investor_data method
        mock_crunchbase.return_value = sample_crunchbase_data

        # Create an InvestorEnricher instance
        enricher = InvestorEnricher()

        # Call the enrich_with_crunchbase method
        enriched_data = enricher.enrich_with_crunchbase(sample_investor_data)

        # Assert that the returned DataFrame contains Crunchbase data
        assert 'total_investments' in enriched_data.columns
        assert 'founded_year' in enriched_data.columns
        assert enriched_data.loc[0, 'total_investments'] == 50
        assert enriched_data.loc[1, 'founded_year'] == 2010

    @patch.object(LinkedinIntegrator, 'fetch_company_data')
    def test_enrich_with_linkedin(self, mock_linkedin, sample_investor_data, sample_linkedin_data):
        # Mock the LinkedIn integrator's fetch_company_data method
        mock_linkedin.return_value = sample_linkedin_data

        # Create an InvestorEnricher instance
        enricher = InvestorEnricher()

        # Call the enrich_with_linkedin method
        enriched_data = enricher.enrich_with_linkedin(sample_investor_data)

        # Assert that the returned DataFrame contains LinkedIn data
        assert 'employees' in enriched_data.columns
        assert 'industry' in enriched_data.columns
        assert enriched_data.loc[0, 'employees'] == 100
        assert enriched_data.loc[1, 'industry'] == 'Private Equity'

    @patch('requests.get')
    def test_enrich_with_web_scraping(self, mock_get, sample_investor_data, sample_html_content):
        # Mock the requests.get method to return sample HTML content
        mock_get.return_value.text = sample_html_content

        # Create an InvestorEnricher instance
        enricher = InvestorEnricher()

        # Call the enrich_with_web_scraping method
        enriched_data = enricher.enrich_with_web_scraping(sample_investor_data)

        # Assert that the returned DataFrame contains scraped data
        assert 'description' in enriched_data.columns
        assert 'Acme Ventures is a leading VC firm in Boston.' in enriched_data.loc[0, 'description']

    def test_merge_enriched_data(self, sample_investor_data):
        # Create sample DataFrames with original and enriched investor data
        crunchbase_data = pd.DataFrame({
            'investor_name': ['Acme Ventures', 'Beta Capital'],
            'total_investments': [50, 30]
        })
        linkedin_data = pd.DataFrame({
            'investor_name': ['Acme Ventures', 'Beta Capital'],
            'employees': [100, 50]
        })

        # Create an InvestorEnricher instance
        enricher = InvestorEnricher()

        # Call the merge_enriched_data method
        merged_data = enricher.merge_enriched_data(sample_investor_data, crunchbase_data, linkedin_data)

        # Assert that the returned DataFrame contains merged data from all sources
        assert 'location' in merged_data.columns
        assert 'total_investments' in merged_data.columns
        assert 'employees' in merged_data.columns
        assert merged_data.loc[0, 'total_investments'] == 50
        assert merged_data.loc[1, 'employees'] == 50

    @patch.object(CrunchbaseIntegrator, 'fetch_portfolio_companies')
    def test_enrich_portfolio_companies(self, mock_portfolio, sample_investor_data, sample_portfolio_companies_data):
        # Mock the Crunchbase integrator's fetch_portfolio_companies method
        mock_portfolio.return_value = sample_portfolio_companies_data

        # Create an InvestorEnricher instance
        enricher = InvestorEnricher()

        # Call the enrich_portfolio_companies method
        enriched_data = enricher.enrich_portfolio_companies(sample_investor_data)

        # Assert that the returned DataFrame contains enriched portfolio data
        assert 'portfolio_companies' in enriched_data.columns
        assert len(enriched_data.loc[0, 'portfolio_companies']) == 2
        assert enriched_data.loc[0, 'portfolio_companies'][0]['name'] == 'TechCo'
        assert enriched_data.loc[1, 'portfolio_companies'][1]['industry'] == 'Renewable Energy'