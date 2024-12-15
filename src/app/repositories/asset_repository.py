from typing import List, Union

from AssetManagement.src.app.config.config import DB
from AssetManagement.src.app.config.types import AssetStatus
from AssetManagement.src.app.models.asset import Asset
from AssetManagement.src.app.models.asset_assigned import AssetAssigned
from AssetManagement.src.app.utils.errors.error import DatabaseError, AssetAlreadyAssignedError
from AssetManagement.src.app.utils.db.query_builder import GenericQueryBuilder


class AssetRepository:
    def __init__(self, database: DB):
        self.db = database

    def add_asset(self, asset: Asset):
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                asset_data = {
                    "serial_number": asset.serial_number,
                    "name": asset.name,
                    "description": asset.description,
                    "status": asset.status
                }
                query, values = GenericQueryBuilder.insert("assets", asset_data)
                cursor.execute(query, values)

        except Exception as e:
            raise DatabaseError(f"Failed to insert asset: {str(e)}")

    def fetch_all_assets(self) -> List[Asset]:
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                columns = ["serial_number", "name", "description", "status"]
                query, values = GenericQueryBuilder.select("assets", columns=columns)
                cursor.execute(query, values)
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
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                columns = ["serial_number", "name", "description", "status"]
                where_clause = {"serial_number": asset_id}
                query, values = GenericQueryBuilder.select(
                    "assets",
                    columns=columns,
                    where=where_clause
                )
                cursor.execute(query, values)
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
            raise DatabaseError(f"Error retrieving assets {str(e)}")

    def assign_asset(self, asset_assigned: AssetAssigned):
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                asset_assign_data = {
                    "user_id": asset_assigned.user_id,
                    "asset_id": asset_assigned.asset_id,
                    "asset_assigned_id": asset_assigned.asset_assigned_id,
                    "assigned_date": asset_assigned.assigned_date
                }
                query, values = GenericQueryBuilder.insert("assets_assigned", asset_assign_data)
                cursor.execute(query, values)

        except Exception as e:
            raise DatabaseError(f"Error assigning asset: {str(e)}")

    def unassign_asset(self, user_id: str, asset_id: str):
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                where_clause = {
                    "user_id": user_id,
                    "asset_id": asset_id
                }
                query, values = GenericQueryBuilder.delete("assets_assigned", where_clause)
                cursor.execute(query, values)

        except Exception as e:
            raise DatabaseError(f"Error unassigning the asset: {str(e)}")

    def update_asset_status(self, asset_id: str, new_asset_status: str) -> None:
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                update_data = {"status": new_asset_status}
                where_clause = {"serial_number": asset_id}
                query, values = GenericQueryBuilder.update("assets", update_data, where_clause)
                cursor.execute(query, values)

        except Exception as e:
            raise DatabaseError(f"Error updating asset: {str(e)}")

    def check_asset_availability(self, asset_id) -> bool:
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                where_clause = {"serial_number": asset_id}
                columns = ["status"]
                query, values = GenericQueryBuilder.select("assets", columns=columns, where=where_clause)
                cursor.execute(query, values)
                result = cursor.fetchone()

                if result is None:
                    return False

                status = result[0] if result else None
                return status == AssetStatus.AVAILABLE.value

        except Exception as e:
            raise AssetAlreadyAssignedError("Asset already assigned")

    def delete_asset(self, asset_id):
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                where_clause = {"serial_number": asset_id}
                query, values = GenericQueryBuilder.delete("assets", where_clause)
                cursor.execute(query, values)

        except Exception as e:
            raise DatabaseError("Failed to delete user")

    def is_asset_assigned(self, user_id: str, asset_id: str) -> bool:
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                where_clause = {
                    "user_id": user_id,
                    "asset_id": asset_id
                }
                columns = ["user_id", "asset_id"]
                query, values = GenericQueryBuilder.select("assets_assigned", columns=columns, where=where_clause)
                cursor.execute(query, values)
                result = cursor.fetchone()

                return True if result else False

        except Exception as e:
            raise DatabaseError("Failed to check assigned asset")

    def view_assigned_assets(self, user_id: str) -> dict:
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT a.serial_number, a.name, a.description, a.status
                    FROM assets a
                    JOIN assets_assigned aa ON a.serial_number = aa.asset_id
                    WHERE aa.user_id = ?
                ''', (user_id,))
                results = cursor.fetchall()

            if not results:
                return {
                    "user_id": user_id,
                    "assets": []
                }

            assets = [
                {
                    "serial_number": row[0],
                    "name": row[1],
                    "description": row[2],
                    "status": row[3]
                } for row in results
            ]

            return {
                "user_id": user_id,
                "assets": assets
            }
        except Exception as e:
            raise DatabaseError(f"Error retrieving assigned assets: {str(e)}")

    def view_all_assigned_assets(self) -> List[dict]:
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT u.id AS user_id, 
                           GROUP_CONCAT(aa.asset_id) AS asset_ids
                    FROM users u
                    JOIN assets_assigned aa ON u.id = aa.user_id
                    GROUP BY u.id
                ''')
                results = cursor.fetchall()

            return [
                {
                    "user_id": row[0],
                    "asset_ids": row[1].split(',') if row[1] else []
                } for row in results
            ]
        except Exception as e:
            raise DatabaseError(f"Error retrieving assigned assets: {str(e)}")