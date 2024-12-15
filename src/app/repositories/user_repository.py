from typing import Optional, List
import sqlite3
from AssetManagement.src.app.models.user import User, UserDTO
from AssetManagement.src.app.config.config import DB
from AssetManagement.src.app.config.types import Role
from AssetManagement.src.app.utils.errors.error import DatabaseError
from AssetManagement.src.app.utils.db.query_builder import GenericQueryBuilder


class UserRepository:
    def __init__(self, database: DB):
        self.db = database

    def save_user(self, user: User) -> None:
        """Saves a new user to the database."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            with conn:
                user_data = {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "password": user.password,
                    "role": user.role,
                    "department": user.department
                }
                query, values = GenericQueryBuilder.insert("users", user_data)
                cursor.execute(query, values)
        except sqlite3.IntegrityError as e:
            raise DatabaseError(f"User creation failed: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Unexpected error during user creation: {str(e)}")

    def delete_user(self, user_id: str) -> bool:
        """Deletes a specific user using id"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            with conn:
                where_clause = {"id": user_id}
                query, values = GenericQueryBuilder.delete("users", where_clause)
                cursor.execute(query, values)

                if cursor.rowcount == 0:
                    return False

            return True

        except Exception as e:
            raise DatabaseError(f"Error deleting user: {str(e)}")

    def fetch_users(self) -> List[UserDTO]:
        """Fetch all users except admin"""
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                where_clause = {"role": Role.USER.value}
                columns = ["id", "name", "email", "department"]
                query, values = GenericQueryBuilder.select(
                    "users",
                    columns=columns,
                    where=where_clause
                )
                cursor.execute(query, values)
                results = cursor.fetchall()

                if results:
                    return [
                        UserDTO(
                            id=result[0],
                            name=result[1],
                            email=result[2],
                            department=result[3]
                        ) for result in results
                    ]
                return []

        except Exception as e:
            raise DatabaseError(f"Error fetching users: {str(e)}")

    def fetch_user_by_email(self, email: str) -> Optional[User]:
        """Fetches a user from the database by their email."""
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                where_clause = {"email": email}
                columns = ["id", "name", "email", "password", "role", "department"]
                query, values = GenericQueryBuilder.select(
                    "users",
                    columns=columns,
                    where=where_clause
                )
                cursor.execute(query, values)
                result = cursor.fetchone()

            if result:
                return User(
                    id=result[0],
                    name=result[1],
                    email=result[2],
                    password=result[3],
                    role=result[4],
                    department=result[5]
                )
            return None
        except Exception as e:
            raise DatabaseError(f"Error fetching user: {str(e)}")

    def fetch_user_by_id(self, user_id: str) -> Optional[User]:
        """Fetches a user from the database by their id."""
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                where_clause = {"id": user_id}
                columns = ["id", "name", "email", "password", "role", "department"]
                query, values = GenericQueryBuilder.select(
                    "users",
                    columns=columns,
                    where=where_clause
                )
                cursor.execute(query, values)
                result = cursor.fetchone()

            if result:
                return User(
                    id=result[0],
                    name=result[1],
                    email=result[2],
                    password=result[3],
                    role=result[4],
                    department=result[5]
                )
            return None
        except Exception as e:
            raise DatabaseError(f"Error fetching user: {str(e)}")