import pytest
from unittest.mock import patch, MagicMock
from src.data_collection.api_integrators.crunchbase_integrator import CrunchbaseIntegrator
from src.backend.models.startup import Startup
from src.backend.models.investor import Investor
from src.backend.models.funding_round import FundingRound
from src.backend.utils.db import db

class TestCrunchbaseIntegrator:

    @pytest.fixture
    def crunchbase_integrator(self):
        return CrunchbaseIntegrator()

    @patch('requests.get')
    def test_fetch_startup_data(self, mock_get, crunchbase_integrator):
        # Mock the API response with sample startup data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'data': {
                'properties': {
                    'name': 'Test Startup',
                    'description': 'A test startup',
                    'founded_on': '2020-01-01',
                    'website': 'https://teststartup.com'
                }
            }
        }
        mock_get.return_value = mock_response

        # Call the fetch_startup_data method with a startup name
        startup_data = crunchbase_integrator.fetch_startup_data('Test Startup')

        # Assert that the API was called with correct parameters
        mock_get.assert_called_once_with(
            'https://api.crunchbase.com/v3.1/organizations/Test Startup',
            params={'user_key': crunchbase_integrator.api_key}
        )

        # Assert that the returned data matches the mocked response
        assert startup_data == mock_response.json()['data']['properties']
        assert 'name' in startup_data
        assert 'description' in startup_data
        assert 'founded_on' in startup_data
        assert 'website' in startup_data

    @patch('requests.get')
    def test_fetch_investor_data(self, mock_get, crunchbase_integrator):
        # Mock the API response with sample investor data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'data': {
                'properties': {
                    'name': 'Test Investor',
                    'description': 'A test investor',
                    'founded_on': '2010-01-01',
                    'website': 'https://testinvestor.com'
                }
            }
        }
        mock_get.return_value = mock_response

        # Call the fetch_investor_data method with an investor name
        investor_data = crunchbase_integrator.fetch_investor_data('Test Investor')

        # Assert that the API was called with correct parameters
        mock_get.assert_called_once_with(
            'https://api.crunchbase.com/v3.1/organizations/Test Investor',
            params={'user_key': crunchbase_integrator.api_key}
        )

        # Assert that the returned data matches the mocked response
        assert investor_data == mock_response.json()['data']['properties']
        assert 'name' in investor_data
        assert 'description' in investor_data
        assert 'founded_on' in investor_data
        assert 'website' in investor_data

    @patch('requests.get')
    def test_fetch_funding_rounds(self, mock_get, crunchbase_integrator):
        # Mock the API response with sample funding rounds data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'data': {
                'items': [
                    {
                        'properties': {
                            'funding_type': 'seed',
                            'announced_on': '2021-01-01',
                            'money_raised': 1000000
                        }
                    }
                ]
            }
        }
        mock_get.return_value = mock_response

        # Call the fetch_funding_rounds method with a startup ID
        funding_rounds = crunchbase_integrator.fetch_funding_rounds('test_startup_id')

        # Assert that the API was called with correct parameters
        mock_get.assert_called_once_with(
            'https://api.crunchbase.com/v3.1/organizations/test_startup_id/funding_rounds',
            params={'user_key': crunchbase_integrator.api_key}
        )

        # Assert that the returned data matches the mocked response
        assert funding_rounds == mock_response.json()['data']['items']
        assert 'funding_type' in funding_rounds[0]['properties']
        assert 'announced_on' in funding_rounds[0]['properties']
        assert 'money_raised' in funding_rounds[0]['properties']

    @patch('src.data_collection.api_integrators.crunchbase_integrator.CrunchbaseIntegrator.fetch_startup_data')
    def test_update_startup_data(self, mock_fetch_startup_data, crunchbase_integrator):
        # Create a mock startup in the database
        startup = Startup(name='Old Startup', description='Old description')
        db.session.add(startup)

        # Mock the fetch_startup_data method to return updated data
        mock_fetch_startup_data.return_value = {
            'name': 'Updated Startup',
            'description': 'Updated description',
            'founded_on': '2020-01-01',
            'website': 'https://updatedstartup.com'
        }

        # Call the update_startup_data method
        crunchbase_integrator.update_startup_data(startup)

        # Assert that the startup in the database was updated
        assert startup.name == 'Updated Startup'
        assert startup.description == 'Updated description'
        assert startup.founded_on == '2020-01-01'
        assert startup.website == 'https://updatedstartup.com'

        # Assert that db.session.commit was called
        db.session.commit.assert_called_once()

    @patch('src.data_collection.api_integrators.crunchbase_integrator.CrunchbaseIntegrator.fetch_investor_data')
    def test_update_investor_data(self, mock_fetch_investor_data, crunchbase_integrator):
        # Create a mock investor in the database
        investor = Investor(name='Old Investor', description='Old description')
        db.session.add(investor)

        # Mock the fetch_investor_data method to return updated data
        mock_fetch_investor_data.return_value = {
            'name': 'Updated Investor',
            'description': 'Updated description',
            'founded_on': '2010-01-01',
            'website': 'https://updatedinvestor.com'
        }

        # Call the update_investor_data method
        crunchbase_integrator.update_investor_data(investor)

        # Assert that the investor in the database was updated
        assert investor.name == 'Updated Investor'
        assert investor.description == 'Updated description'
        assert investor.founded_on == '2010-01-01'
        assert investor.website == 'https://updatedinvestor.com'

        # Assert that db.session.commit was called
        db.session.commit.assert_called_once()