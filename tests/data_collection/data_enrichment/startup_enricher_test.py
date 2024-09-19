import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.data_collection.data_enrichment.startup_enricher import StartupEnricher
from src.data_collection.api_integrators.crunchbase_integrator import CrunchbaseIntegrator
from src.data_collection.api_integrators.linkedin_integrator import LinkedinIntegrator

class StartupEnricherTests:
    @pytest.fixture
    def sample_startup_data(self):
        # Create a sample DataFrame with startup data
        return pd.DataFrame({
            'name': ['Startup A', 'Startup B'],
            'website': ['www.startupa.com', 'www.startupb.com']
        })

    @pytest.fixture
    def sample_crunchbase_data(self):
        # Create sample Crunchbase data
        return pd.DataFrame({
            'name': ['Startup A', 'Startup B'],
            'funding_total': [1000000, 2000000],
            'founded_on': ['2020-01-01', '2019-01-01']
        })

    @pytest.fixture
    def sample_linkedin_data(self):
        # Create sample LinkedIn data
        return pd.DataFrame({
            'name': ['Startup A', 'Startup B'],
            'employee_count': [50, 100],
            'industry': ['Tech', 'Finance']
        })

    @pytest.fixture
    def sample_html_content(self):
        # Create sample HTML content for web scraping
        return "<html><body><h1>Startup A</h1><p>Description: AI-powered solution</p></body></html>"

    @patch.object(CrunchbaseIntegrator, 'fetch_startup_data')
    @patch.object(LinkedinIntegrator, 'fetch_company_data')
    def test_enrich_startup_data(self, mock_linkedin, mock_crunchbase, sample_startup_data, sample_crunchbase_data, sample_linkedin_data):
        # Mock the Crunchbase and LinkedIn integrators
        mock_crunchbase.return_value = sample_crunchbase_data
        mock_linkedin.return_value = sample_linkedin_data

        # Create a StartupEnricher instance
        enricher = StartupEnricher()

        # Call the enrich_startup_data method
        enriched_data = enricher.enrich_startup_data(sample_startup_data)

        # Assert that the returned DataFrame has the expected enriched data
        assert 'funding_total' in enriched_data.columns
        assert 'employee_count' in enriched_data.columns
        assert enriched_data['funding_total'].tolist() == [1000000, 2000000]
        assert enriched_data['employee_count'].tolist() == [50, 100]

    @patch.object(CrunchbaseIntegrator, 'fetch_startup_data')
    def test_enrich_with_crunchbase(self, mock_crunchbase, sample_startup_data, sample_crunchbase_data):
        # Mock the Crunchbase integrator's fetch_startup_data method
        mock_crunchbase.return_value = sample_crunchbase_data

        # Create a StartupEnricher instance
        enricher = StartupEnricher()

        # Call the enrich_with_crunchbase method
        enriched_data = enricher.enrich_with_crunchbase(sample_startup_data)

        # Assert that the returned DataFrame contains Crunchbase data
        assert 'funding_total' in enriched_data.columns
        assert 'founded_on' in enriched_data.columns
        assert enriched_data['funding_total'].tolist() == [1000000, 2000000]
        assert enriched_data['founded_on'].tolist() == ['2020-01-01', '2019-01-01']

    @patch.object(LinkedinIntegrator, 'fetch_company_data')
    def test_enrich_with_linkedin(self, mock_linkedin, sample_startup_data, sample_linkedin_data):
        # Mock the LinkedIn integrator's fetch_company_data method
        mock_linkedin.return_value = sample_linkedin_data

        # Create a StartupEnricher instance
        enricher = StartupEnricher()

        # Call the enrich_with_linkedin method
        enriched_data = enricher.enrich_with_linkedin(sample_startup_data)

        # Assert that the returned DataFrame contains LinkedIn data
        assert 'employee_count' in enriched_data.columns
        assert 'industry' in enriched_data.columns
        assert enriched_data['employee_count'].tolist() == [50, 100]
        assert enriched_data['industry'].tolist() == ['Tech', 'Finance']

    @patch('requests.get')
    def test_enrich_with_web_scraping(self, mock_get, sample_startup_data, sample_html_content):
        # Mock the requests.get method to return sample HTML content
        mock_get.return_value = MagicMock(text=sample_html_content)

        # Create a StartupEnricher instance
        enricher = StartupEnricher()

        # Call the enrich_with_web_scraping method
        enriched_data = enricher.enrich_with_web_scraping(sample_startup_data)

        # Assert that the returned DataFrame contains scraped data
        assert 'description' in enriched_data.columns
        assert enriched_data['description'].iloc[0] == 'AI-powered solution'

    def test_merge_enriched_data(self, sample_startup_data):
        # Create sample DataFrames with original and enriched data
        crunchbase_data = pd.DataFrame({
            'name': ['Startup A', 'Startup B'],
            'funding_total': [1000000, 2000000]
        })
        linkedin_data = pd.DataFrame({
            'name': ['Startup A', 'Startup B'],
            'employee_count': [50, 100]
        })
        scraped_data = pd.DataFrame({
            'name': ['Startup A', 'Startup B'],
            'description': ['AI solution', 'Fintech platform']
        })

        # Create a StartupEnricher instance
        enricher = StartupEnricher()

        # Call the merge_enriched_data method
        merged_data = enricher.merge_enriched_data(sample_startup_data, crunchbase_data, linkedin_data, scraped_data)

        # Assert that the returned DataFrame contains merged data from all sources
        assert 'website' in merged_data.columns
        assert 'funding_total' in merged_data.columns
        assert 'employee_count' in merged_data.columns
        assert 'description' in merged_data.columns
        assert merged_data['funding_total'].tolist() == [1000000, 2000000]
        assert merged_data['employee_count'].tolist() == [50, 100]
        assert merged_data['description'].tolist() == ['AI solution', 'Fintech platform']