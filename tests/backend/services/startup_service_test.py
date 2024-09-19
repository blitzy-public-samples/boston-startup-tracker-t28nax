import pytest
from unittest.mock import patch, MagicMock
from src.backend.services import startup_service
from src.backend.models.startup import Startup
from src.backend.utils import db

class TestStartupService:
    @patch('src.backend.utils.db.session.query')
    def test_get_startups(self, mock_query):
        # Mock db.session.query to return a list of mock startups
        mock_startups = [Startup(id=1, name='Startup 1'), Startup(id=2, name='Startup 2')]
        mock_query.return_value.all.return_value = mock_startups

        # Call startup_service.get_startups()
        result = startup_service.get_startups()

        # Assert the correct number of startups is returned
        assert len(result) == len(mock_startups)

        # Assert the returned objects are of type Startup
        for startup in result:
            assert isinstance(startup, Startup)

    @patch('src.backend.utils.db.session.query')
    def test_get_startup_by_id(self, mock_query):
        # Create a mock startup with a specific ID
        mock_startup = Startup(id=1, name='Test Startup')
        mock_query.return_value.get.return_value = mock_startup

        # Call startup_service.get_startup_by_id() with the specific ID
        result = startup_service.get_startup_by_id(1)

        # Assert the returned startup matches the mock startup
        assert result == mock_startup

        # Assert the returned object is an instance of Startup
        assert isinstance(result, Startup)

    @patch('src.backend.utils.db.session.add')
    @patch('src.backend.utils.db.session.commit')
    def test_create_startup(self, mock_commit, mock_add):
        # Create mock startup data
        startup_data = {'name': 'New Startup', 'description': 'A new startup'}

        # Call startup_service.create_startup() with mock data
        result = startup_service.create_startup(startup_data)

        # Assert db.session.add was called with a Startup object
        mock_add.assert_called_once()
        assert isinstance(mock_add.call_args[0][0], Startup)

        # Assert db.session.commit was called
        mock_commit.assert_called_once()

        # Assert the returned object is an instance of Startup
        assert isinstance(result, Startup)

    @patch('src.backend.utils.db.session.query')
    @patch('src.backend.utils.db.session.commit')
    def test_update_startup(self, mock_commit, mock_query):
        # Create a mock startup
        mock_startup = Startup(id=1, name='Old Name', description='Old description')
        mock_query.return_value.get.return_value = mock_startup

        # Create mock update data
        update_data = {'name': 'New Name', 'description': 'New description'}

        # Call startup_service.update_startup() with mock data
        result = startup_service.update_startup(1, update_data)

        # Assert the startup's attributes are updated
        assert result.name == 'New Name'
        assert result.description == 'New description'

        # Assert db.session.commit was called
        mock_commit.assert_called_once()

        # Assert the returned object is an instance of Startup
        assert isinstance(result, Startup)

    @patch('src.backend.utils.db.session.query')
    @patch('src.backend.utils.db.session.delete')
    @patch('src.backend.utils.db.session.commit')
    def test_delete_startup(self, mock_commit, mock_delete, mock_query):
        # Create a mock startup
        mock_startup = Startup(id=1, name='Startup to delete')
        mock_query.return_value.get.return_value = mock_startup

        # Call startup_service.delete_startup() with the startup's ID
        startup_service.delete_startup(1)

        # Assert db.session.delete was called with the mock startup
        mock_delete.assert_called_once_with(mock_startup)

        # Assert db.session.commit was called
        mock_commit.assert_called_once()