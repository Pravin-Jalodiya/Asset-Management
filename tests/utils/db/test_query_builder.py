import unittest

from src.app.utils.db.query_builder import GenericQueryBuilder


class TestGenericQueryBuilder(unittest.TestCase):
    def test_insert_single_column(self):
        """Test insert method with a single column"""
        table = "users"
        data = {"name": "John"}
        expected_query = "INSERT INTO users (name) VALUES (?)"
        expected_values = ["John"]
        query, values = GenericQueryBuilder.insert(table, data)
        self.assertEqual(query, expected_query)
        self.assertEqual(values, expected_values)

    def test_insert_multiple_columns(self):
        """Test insert method with multiple columns"""
        table = "users"
        data = {"name": "John", "age": 30, "email": "john@example.com"}
        expected_query = "INSERT INTO users (name, age, email) VALUES (?, ?, ?)"
        expected_values = ["John", 30, "john@example.com"]
        query, values = GenericQueryBuilder.insert(table, data)
        self.assertEqual(query, expected_query)
        self.assertEqual(values, expected_values)

    def test_update_single_column(self):
        """Test update method with a single column to update"""
        table = "users"
        data = {"name": "John Doe"}
        where = {"id": 1}
        expected_query = "UPDATE users SET name = ? WHERE id = ?"
        expected_values = ["John Doe", 1]
        query, values = GenericQueryBuilder.update(table, data, where)
        self.assertEqual(query, expected_query)
        self.assertEqual(values, expected_values)

    def test_update_multiple_columns(self):
        """Test update method with multiple columns to update"""
        table = "users"
        data = {"name": "John Doe", "age": 31}
        where = {"id": 1}
        expected_query = "UPDATE users SET name = ?, age = ? WHERE id = ?"
        expected_values = ["John Doe", 31, 1]
        query, values = GenericQueryBuilder.update(table, data, where)
        self.assertEqual(query, expected_query)
        self.assertEqual(values, expected_values)

    def test_update_multiple_where_conditions(self):
        """Test update method with multiple where conditions"""
        table = "users"
        data = {"name": "John Doe"}
        where = {"active": 1, "department": "sales"}
        expected_query = "UPDATE users SET name = ? WHERE active = ? AND department = ?"
        expected_values = ["John Doe", 1, "sales"]
        query, values = GenericQueryBuilder.update(table, data, where)
        self.assertEqual(query, expected_query)
        self.assertEqual(values, expected_values)

    def test_delete_single_condition(self):
        """Test delete method with a single where condition"""
        table = "users"
        where = {"id": 1}
        expected_query = "DELETE FROM users WHERE id = ?"
        expected_values = [1]
        query, values = GenericQueryBuilder.delete(table, where)
        self.assertEqual(query, expected_query)
        self.assertEqual(values, expected_values)

    def test_delete_multiple_conditions(self):
        """Test delete method with multiple where conditions"""
        table = "users"
        where = {"active": 0, "department": "sales"}
        expected_query = "DELETE FROM users WHERE active = ? AND department = ?"
        expected_values = [0, "sales"]
        query, values = GenericQueryBuilder.delete(table, where)
        self.assertEqual(query, expected_query)
        self.assertEqual(values, expected_values)

    def test_delete_without_where_clause(self):
        """Test delete method without a where clause"""
        table = "users"
        expected_query = "DELETE FROM users"
        expected_values = []
        query, values = GenericQueryBuilder.delete(table)
        self.assertEqual(query, expected_query)
        self.assertEqual(values, expected_values)

    def test_select_all_columns(self):
        """Test select method retrieving all columns"""
        table = "users"
        expected_query = "SELECT * FROM users"
        expected_values = []
        query, values = GenericQueryBuilder.select(table)
        self.assertEqual(query, expected_query)
        self.assertEqual(values, expected_values)

    def test_select_specific_columns(self):
        """Test select method with specific columns"""
        table = "users"
        columns = ["id", "name", "email"]
        expected_query = "SELECT id, name, email FROM users"
        expected_values = []
        query, values = GenericQueryBuilder.select(table, columns)
        self.assertEqual(query, expected_query)
        self.assertEqual(values, expected_values)

    def test_select_with_where_clause(self):
        """Test select method with a single where condition"""
        table = "users"
        where = {"active": 1}
        expected_query = "SELECT * FROM users WHERE active = ?"
        expected_values = [1]
        query, values = GenericQueryBuilder.select(table, where=where)
        self.assertEqual(query, expected_query)
        self.assertEqual(values, expected_values)

    def test_select_with_multiple_where_conditions(self):
        """Test select method with multiple where conditions"""
        table = "users"
        where = {"active": 1, "department": "sales"}
        expected_query = "SELECT * FROM users WHERE active = ? AND department = ?"
        expected_values = [1, "sales"]
        query, values = GenericQueryBuilder.select(table, where=where)
        self.assertEqual(query, expected_query)
        self.assertEqual(values, expected_values)

    def test_select_with_order_by(self):
        """Test select method with order by clause"""
        table = "users"
        order_by = "id"
        expected_query = "SELECT * FROM users ORDER BY id DESC"
        expected_values = []
        query, values = GenericQueryBuilder.select(table, order_by=order_by)
        self.assertEqual(query, expected_query)
        self.assertEqual(values, expected_values)

    def test_select_with_limit(self):
        """Test select method with limit clause"""
        table = "users"
        limit = 10
        expected_query = "SELECT * FROM users LIMIT 10"
        expected_values = []
        query, values = GenericQueryBuilder.select(table, limit=limit)
        self.assertEqual(query, expected_query)
        self.assertEqual(values, expected_values)

    def test_select_with_all_parameters(self):
        """Test select method with all optional parameters"""
        table = "users"
        columns = ["id", "name", "email"]
        where = {"active": 1}
        order_by = "id"
        limit = 10
        expected_query = "SELECT id, name, email FROM users WHERE active = ? ORDER BY id DESC LIMIT 10"
        expected_values = [1]
        query, values = GenericQueryBuilder.select(table, columns, where, order_by, limit)
        self.assertEqual(query, expected_query)
        self.assertEqual(values, expected_values)
