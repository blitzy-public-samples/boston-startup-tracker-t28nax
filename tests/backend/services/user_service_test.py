import pytest
from unittest.mock import patch, MagicMock
from src.backend.services import user_service
from src.backend.models.user import User
from src.backend.utils import db
from src.backend.utils import auth as bcrypt

class TestUserService:
    @pytest.fixture
    def mock_db_session(self):
        with patch('src.backend.utils.db.session') as mock_session:
            yield mock_session

    @pytest.fixture
    def mock_bcrypt(self):
        with patch('src.backend.utils.auth.bcrypt') as mock_bcrypt:
            yield mock_bcrypt

    def test_get_users(self, mock_db_session):
        # Mock db.session.query to return a list of mock users
        mock_users = [User(id=1, username='user1'), User(id=2, username='user2')]
        mock_db_session.query.return_value.all.return_value = mock_users

        # Call user_service.get_users()
        result = user_service.get_users()

        # Assert the correct number of users is returned
        assert len(result) == len(mock_users)

        # Assert the returned objects are of type User
        assert all(isinstance(user, User) for user in result)

    def test_get_user_by_id(self, mock_db_session):
        # Create a mock user with a specific ID
        mock_user = User(id=1, username='testuser')
        mock_db_session.query.return_value.get.return_value = mock_user

        # Call user_service.get_user_by_id() with the specific ID
        result = user_service.get_user_by_id(1)

        # Assert the returned user matches the mock user
        assert result == mock_user

        # Assert the returned object is an instance of User
        assert isinstance(result, User)

    def test_create_user(self, mock_db_session, mock_bcrypt):
        # Create mock user data
        user_data = {'username': 'newuser', 'email': 'newuser@example.com', 'password': 'password123'}

        # Mock bcrypt.generate_password_hash
        mock_bcrypt.generate_password_hash.return_value = b'hashed_password'

        # Call user_service.create_user() with mock data
        result = user_service.create_user(user_data)

        # Assert bcrypt.generate_password_hash was called
        mock_bcrypt.generate_password_hash.assert_called_once_with('password123')

        # Assert db.session.add was called with a User object
        mock_db_session.add.assert_called_once()
        added_user = mock_db_session.add.call_args[0][0]
        assert isinstance(added_user, User)

        # Assert db.session.commit was called
        mock_db_session.commit.assert_called_once()

        # Assert the returned object is an instance of User
        assert isinstance(result, User)

    def test_update_user(self, mock_db_session):
        # Create a mock user
        mock_user = User(id=1, username='oldusername', email='old@example.com')
        mock_db_session.query.return_value.get.return_value = mock_user

        # Create mock update data
        update_data = {'username': 'newusername', 'email': 'new@example.com'}

        # Call user_service.update_user() with mock data
        result = user_service.update_user(1, update_data)

        # Assert the user's attributes are updated
        assert result.username == 'newusername'
        assert result.email == 'new@example.com'

        # Assert db.session.commit was called
        mock_db_session.commit.assert_called_once()

        # Assert the returned object is an instance of User
        assert isinstance(result, User)

    def test_delete_user(self, mock_db_session):
        # Create a mock user
        mock_user = User(id=1, username='testuser')
        mock_db_session.query.return_value.get.return_value = mock_user

        # Call user_service.delete_user() with the user's ID
        user_service.delete_user(1)

        # Assert db.session.delete was called with the mock user
        mock_db_session.delete.assert_called_once_with(mock_user)

        # Assert db.session.commit was called
        mock_db_session.commit.assert_called_once()

    def test_authenticate_user(self, mock_db_session, mock_bcrypt):
        # Create a mock user with a hashed password
        mock_user = User(id=1, username='testuser', password='hashed_password')
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_user

        # Mock bcrypt.check_password_hash to return True
        mock_bcrypt.check_password_hash.return_value = True

        # Call user_service.authenticate_user() with correct credentials
        result = user_service.authenticate_user('testuser', 'password123')

        # Assert bcrypt.check_password_hash was called
        mock_bcrypt.check_password_hash.assert_called_once_with('hashed_password', 'password123')

        # Assert the returned user matches the mock user
        assert result == mock_user