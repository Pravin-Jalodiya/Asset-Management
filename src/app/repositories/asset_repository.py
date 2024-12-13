from typing import List, Union

from AssetManagement.src.app.config.config import DB
from AssetManagement.src.app.config.types import AssetStatus
from AssetManagement.src.app.models.asset import Asset
from AssetManagement.src.app.utils.errors.error import DatabaseError, AssetAlreadyAssignedError


class AssetRepository:
    def __init__(self, database: DB):
        self.db = database

    def add_asset(self, asset: Asset):
        """
        Add a new asset to assets table
        """
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO assets (
                    a.serial_number, 
                    a.name, 
                    a.description, 
                    a.status
                ) VALUES (?, ?, ?, ?);
                ''', (
                    asset.serial_number,
                    asset.name,
                    asset.description,
                    asset.status
                    )
                )

        except Exception as e:
            raise DatabaseError("Failed to insert asset")


    def fetch_all_assets(self) -> List[Asset]:
        """
        Retrieves all assets
        """
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT a.serial_number, a.name, a.description, a.status
                    FROM assets a
                ''')

                results = cursor.fetchall()

                return [
                    Asset(
                        serial_number=row[0],
                        name=row[1],
                        description=row[2],
                        status=row[3]
                    ) for row in results
                ]

        except Exception as e:
            raise DatabaseError("Error retrieving assets")

    def fetch_asset_by_id(self, asset_id: str) -> Union[Asset, None]:
        """
        Retrieves all assets
        """
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT a.serial_number, a.name, a.description, a.status
                    FROM assets a
                    WHERE a.serial_number = ?
                ''', asset_id)

                result = cursor.fetchone()

                if result is not None:
                    return Asset(
                            serial_number=result[0],
                            name=result[1],
                            description=result[2],
                            status=result[3]
                        )

                else:
                    return None


        except Exception as e:
            raise DatabaseError("Error retrieving assets")

    def view_assigned_assets(self, user_id: str) -> List[Asset]:
        """Retrieves all assets assigned to a specific user."""
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT a.serial_number, a.name, a.description, a.status
                    FROM assets a
                    JOIN assets_assigned aa ON a.serial_number = aa.asset_id
                    WHERE aa.user_id = ?;
                ''', (user_id,))
                results = cursor.fetchall()

            return [
                Asset(
                    serial_number=row[0],
                    name=row[1],
                    description=row[2],
                    status=row[3]
                ) for row in results
            ]
        except Exception as e:
            raise DatabaseError(f"Error retrieving assigned assets: {str(e)}")

    def assign_asset(self, user_id: str, asset_id: str):
        """
        Assigns an asset to a user.
        """
        try:
            conn = self.db.get_connetion()
            with conn:
                cursor = self.db.get_connection()
                # Assign the asset to user if available
                cursor.execute('''
                INSERT INTO asset_assigned (
                user_id, asset_id
                ) VALUES (? , ?);
                ''', (user_id, asset_id))

        except Exception as e:
            raise DatabaseError(f"Error assigning asset: {str(e)}")

    def unassign_asset(self, user_id: str, asset_id: str):
        """
        Unassigns an asset to a user
        """
        try:
            conn = self.db.get_connection()
            with conn:
                # Remove asset assignment
                cursor = conn.cursor()
                cursor.execute(
                    'DELETE FROM assets_assigned WHERE user_id = ? AND asset_id = ?',
                    (user_id, asset_id)
                )

        except Exception as e:
            raise DatabaseError(f"Error unassigning the asset: {str(e)}")

    def update_asset_status(self, asset_id: str, new_asset_status: str) -> None:
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = self.db.get_connection()
                # Update the asset status
                cursor.execute(
                    'UPDATE assets SET status = ? WHERE serial_number = ?',
                    (new_asset_status, asset_id)
                )

                return

        except Exception as e:
            raise DatabaseError(f"Error updating asset: {str(e)}")

    def check_asset_availability(self, asset_id) -> bool:
        try:
            conn = self.db.get_connetion()
            with conn:
                cursor = conn.cursor()
                cursor.execute('''
                           SELECT a.status
                           FROM assets a
                           WHERE a.serial_number = ?
                       ''', (asset_id,))

                status = cursor.fetchone()

                return status == AssetStatus.AVAILABLE.value

        except Exception as e:
            raise AssetAlreadyAssignedError("Asset already assigned")

    def delete_asset(self, asset_id):
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM assets WHERE serial_number = ?
                ''', asset_id)

        except Exception as e:
            raise DatabaseError("Failed to delete user")

    def is_asset_assigned(self, user_id: str, asset_id: str) -> bool:
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, asset_id
                    FROM assets_assigned
                    WHERE user_id = ? AND asset_id = ?
                ''', (user_id, asset_id))

                if cursor.rowcount == 0:
                    return False

                return True

        except Exception as e:
            raise DatabaseError("Failed to check assigned asset")



