from typing import Optional, List
import sqlite3
from AssetManagement.src.app.models.user import User, UserDTO
from AssetManagement.src.app.config.config import DB
from AssetManagement.src.app.config.types import Role
from AssetManagement.src.app.utils.errors.error import DatabaseError


class UserRepository:
    def __init__(self, database: DB):
        self.db = database

    def save_user(self, user: User) -> None:
        """Saves a new user to the database."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            with conn:
                cursor.execute('''
                    INSERT INTO users (id, name, email, password, role, department)
                    VALUES (?, ?, ?, ?, ?, ?);
                ''', (user.id, user.name, user.email, user.password, user.role, user.department))
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
                cursor.execute('''
                DELETE FROM users
                WHERE id = (?)
                ''', (user_id,))

            if cursor.rowcount == 0:
                return False

            return True

        except Exception as e:
            raise DatabaseError("")


    def fetch_users(self) -> List[UserDTO]:
        """Fetch all users except admin"""
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    '''
                    SELECT id, name, email, department
                    FROM users
                    WHERE role = ?
                    ''',
                    (Role.USER.value,)
                )

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
            print(e)
            raise DatabaseError(f"Error fetching users: {str(e)}")

    def fetch_user_by_email(self, email: str) -> Optional[User]:
        """Fetches a user from the database by their email."""
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, email, password, role, department
                    FROM users
                    WHERE email = ?;
                ''', (email,))
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
                cursor.execute('''
                    SELECT id, name, email, password, role, department
                    FROM users
                    WHERE id = ?;
                ''', (user_id,))
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