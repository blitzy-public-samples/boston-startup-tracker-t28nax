import pytest
from unittest.mock import patch, MagicMock
from src.backend.services import investor_service
from src.backend.models.investor import Investor
from src.backend.utils import db

class TestInvestorService:
    @patch('src.backend.utils.db.session.query')
    def test_get_investors(self, mock_query):
        # Mock db.session.query to return a list of mock investors
        mock_investors = [Investor(id=1, name="Investor 1"), Investor(id=2, name="Investor 2")]
        mock_query.return_value.all.return_value = mock_investors

        # Call investor_service.get_investors()
        result = investor_service.get_investors()

        # Assert the correct number of investors is returned
        assert len(result) == len(mock_investors)

        # Assert the returned objects are of type Investor
        for investor in result:
            assert isinstance(investor, Investor)

    @patch('src.backend.utils.db.session.query')
    def test_get_investor_by_id(self, mock_query):
        # Create a mock investor with a specific ID
        mock_investor = Investor(id=1, name="Test Investor")
        mock_query.return_value.get.return_value = mock_investor

        # Call investor_service.get_investor_by_id() with the specific ID
        result = investor_service.get_investor_by_id(1)

        # Assert the returned investor matches the mock investor
        assert result == mock_investor

        # Assert the returned object is an instance of Investor
        assert isinstance(result, Investor)

    @patch('src.backend.utils.db.session.add')
    @patch('src.backend.utils.db.session.commit')
    def test_create_investor(self, mock_commit, mock_add):
        # Create mock investor data
        investor_data = {"name": "New Investor", "email": "new@investor.com"}

        # Call investor_service.create_investor() with mock data
        result = investor_service.create_investor(investor_data)

        # Assert db.session.add was called with an Investor object
        mock_add.assert_called_once()
        assert isinstance(mock_add.call_args[0][0], Investor)

        # Assert db.session.commit was called
        mock_commit.assert_called_once()

        # Assert the returned object is an instance of Investor
        assert isinstance(result, Investor)

    @patch('src.backend.utils.db.session.query')
    @patch('src.backend.utils.db.session.commit')
    def test_update_investor(self, mock_commit, mock_query):
        # Create a mock investor
        mock_investor = Investor(id=1, name="Old Name", email="old@email.com")
        mock_query.return_value.get.return_value = mock_investor

        # Create mock update data
        update_data = {"name": "New Name", "email": "new@email.com"}

        # Call investor_service.update_investor() with mock data
        result = investor_service.update_investor(1, update_data)

        # Assert the investor's attributes are updated
        assert result.name == update_data["name"]
        assert result.email == update_data["email"]

        # Assert db.session.commit was called
        mock_commit.assert_called_once()

        # Assert the returned object is an instance of Investor
        assert isinstance(result, Investor)

    @patch('src.backend.utils.db.session.query')
    @patch('src.backend.utils.db.session.delete')
    @patch('src.backend.utils.db.session.commit')
    def test_delete_investor(self, mock_commit, mock_delete, mock_query):
        # Create a mock investor
        mock_investor = Investor(id=1, name="To Be Deleted")
        mock_query.return_value.get.return_value = mock_investor

        # Call investor_service.delete_investor() with the investor's ID
        investor_service.delete_investor(1)

        # Assert db.session.delete was called with the mock investor
        mock_delete.assert_called_once_with(mock_investor)

        # Assert db.session.commit was called
        mock_commit.assert_called_once()