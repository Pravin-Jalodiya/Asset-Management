import unittest
from unittest.mock import MagicMock, patch
from src.app.repositories.user_repository import UserRepository
from src.app.models.user import User, UserDTO
from src.app.utils.errors.error import DatabaseError
from src.app.config.types import Role


class TestUserRepository(unittest.TestCase):
    @patch("src.app.utils.db.db.DB")
    @patch("src.app.utils.db.query_builder.GenericQueryBuilder")
    def setUp(self, mock_query_builder, mock_db):
        # Initialize mocked DB and QueryBuilder
        self.mock_db = mock_db
        self.mock_query_builder = mock_query_builder

        # Mock DB connection and cursor
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_db.get_connection.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cursor

        # Initialize UserRepository with mocked DB
        self.user_repository = UserRepository(self.mock_db)

    def test_save_user_success(self):
        # Arrange
        user = User(
            id="U001",
            name="John Doe",
            email="john@example.com",
            password="hashed_password",
            role=Role.USER.value,
            department="IT"
        )

        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "password": user.password,
            "role": user.role,
            "department": user.department
        }

        query = "INSERT INTO users (id, name, email, password, role, department) VALUES (?, ?, ?, ?, ?, ?)"
        values = list(user_data.values())
        self.mock_query_builder.insert.return_value = (query, values)

        # Act
        self.user_repository.save_user(user)

        # Assert
        self.mock_cursor.execute.assert_called_once_with(query, values)

    def test_save_user_database_error(self):
        # Arrange
        user = User(
            id="U001",
            name="John Doe",
            email="john@example.com",
            password="hashed_password",
            role=Role.USER.value,
            department="IT"
        )
        self.mock_conn.cursor.side_effect = Exception("Database connection error")

        # Act & Assert
        with self.assertRaises(DatabaseError):
            self.user_repository.save_user(user)

    def test_delete_user_success(self):
        # Arrange
        user_id = "U001"
        query = "DELETE FROM users WHERE id = ?"
        values = (user_id,)
        self.mock_query_builder.delete.return_value = (query, values)
        self.mock_cursor.rowcount = 1

        # Act
        result = self.user_repository.delete_user(user_id)

        # Assert
        self.assertTrue(result)
        self.mock_cursor.execute.assert_called_once()

    def test_delete_user_not_found(self):
        # Arrange
        user_id = "U999"
        query = "DELETE FROM users WHERE id = ?"
        values = (user_id,)
        self.mock_query_builder.delete.return_value = (query, values)
        self.mock_cursor.rowcount = 0

        # Act
        result = self.user_repository.delete_user(user_id)

        # Assert
        self.assertFalse(result)
        self.mock_cursor.execute.assert_called_once()

    def test_delete_user_database_error(self):
        # Arrange
        user_id = "U001"
        self.mock_conn.cursor.side_effect = Exception("Database connection error")

        # Act & Assert
        with self.assertRaises(DatabaseError):
            self.user_repository.delete_user(user_id)

    def test_fetch_users_success(self):
        # Arrange
        mock_results = [
            ("U001", "John Doe", "john@example.com", "IT"),
            ("U002", "Jane Smith", "jane@example.com", "HR")
        ]
        self.mock_cursor.fetchall.return_value = mock_results

        columns = ["id", "name", "email", "department"]
        where_clause = {"role": Role.USER.value}
        query = "SELECT id, name, email, department FROM users WHERE role = ?"
        values = (Role.USER.value,)
        self.mock_query_builder.select.return_value = (query, values)

        # Act
        users = self.user_repository.fetch_users()

        # Assert
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0].id, "U001")
        self.assertEqual(users[1].name, "Jane Smith")
        self.assertIsInstance(users[0], UserDTO)

    def test_fetch_users_empty_list(self):
        # Arrange
        self.mock_cursor.fetchall.return_value = []
        where_clause = {"role": Role.USER.value}
        query = "SELECT id, name, email, department FROM users WHERE role = ?"
        values = (Role.USER.value,)
        self.mock_query_builder.select.return_value = (query, values)

        # Act
        users = self.user_repository.fetch_users()

        # Assert
        self.assertEqual(len(users), 0)

    def test_fetch_users_database_error(self):
        # Arrange
        self.mock_conn.cursor.side_effect = Exception("Database connection error")

        # Act & Assert
        with self.assertRaises(DatabaseError):
            self.user_repository.fetch_users()

    def test_fetch_user_by_email_success(self):
        # Arrange
        email = "john@example.com"
        mock_result = ("U001", "John Doe", "john@example.com", "hashed_password", Role.USER.value, "IT")
        self.mock_cursor.fetchone.return_value = mock_result

        columns = ["id", "name", "email", "password", "role", "department"]
        where_clause = {"email": email}
        query = "SELECT id, name, email, password, role, department FROM users WHERE email = ?"
        values = (email,)
        self.mock_query_builder.select.return_value = (query, values)

        # Act
        user = self.user_repository.fetch_user_by_email(email)

        # Assert
        self.assertIsNotNone(user)
        self.assertEqual(user.email, email)
        self.assertEqual(user.name, "John Doe")
        self.assertIsInstance(user, User)

    def test_fetch_user_by_email_not_found(self):
        # Arrange
        email = "nonexistent@example.com"
        self.mock_cursor.fetchone.return_value = None

        columns = ["id", "name", "email", "password", "role", "department"]
        where_clause = {"email": email}
        query = "SELECT id, name, email, password, role, department FROM users WHERE email = ?"
        values = (email,)
        self.mock_query_builder.select.return_value = (query, values)

        # Act
        user = self.user_repository.fetch_user_by_email(email)

        # Assert
        self.assertIsNone(user)

    def test_fetch_user_by_email_database_error(self):
        # Arrange
        email = "john@example.com"
        self.mock_conn.cursor.side_effect = Exception("Database connection error")

        # Act & Assert
        with self.assertRaises(DatabaseError):
            self.user_repository.fetch_user_by_email(email)

    def test_fetch_user_by_id_success(self):
        # Arrange
        user_id = "U001"
        mock_result = ("U001", "John Doe", "john@example.com", "IT")
        self.mock_cursor.fetchone.return_value = mock_result

        columns = ["id", "name", "email", "department"]
        where_clause = {"id": user_id}
        query = "SELECT id, name, email, department FROM users WHERE id = ?"
        values = (user_id,)
        self.mock_query_builder.select.return_value = (query, values)

        # Act
        user = self.user_repository.fetch_user_by_id(user_id)

        # Assert
        self.assertIsNotNone(user)
        self.assertEqual(user.id, user_id)
        self.assertEqual(user.name, "John Doe")
        self.assertIsInstance(user, UserDTO)

    def test_fetch_user_by_id_not_found(self):
        # Arrange
        user_id = "U999"
        self.mock_cursor.fetchone.return_value = None

        columns = ["id", "name", "email", "department"]
        where_clause = {"id": user_id}
        query = "SELECT id, name, email, department FROM users WHERE id = ?"
        values = (user_id,)
        self.mock_query_builder.select.return_value = (query, values)

        # Act
        user = self.user_repository.fetch_user_by_id(user_id)

        # Assert
        self.assertIsNone(user)

    def test_fetch_user_by_id_database_error(self):
        # Arrange
        user_id = "U001"
        self.mock_conn.cursor.side_effect = Exception("Database connection error")

        # Act & Assert
        with self.assertRaises(DatabaseError):
            self.user_repository.fetch_user_by_id(user_id)