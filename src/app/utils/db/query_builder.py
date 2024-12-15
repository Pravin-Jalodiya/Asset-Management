from typing import List, Dict, Optional


class GenericQueryBuilder:

    @staticmethod
    def insert(table: str, data: Dict[str, any]):

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = list(data.values())
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return query, values

    @staticmethod
    def update(table: str, data: Dict[str, any], where: Optional[Dict[str, any]] = None):

        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {table} SET {set_clause}"
        if where:
            where_clause = ", ".join([f"{key} = ?" for key in where.keys()])
            query += f" WHERE {where_clause}"
        values = list(data.values()) + list(where.values())
        return query, values

    @staticmethod
    def delete(table: str, where: Optional[Dict[str, any]] = None):

        query = f"DELETE FROM {table}"
        if where:
            where_clause = "AND ".join([f"{key} = ?" for key in where.keys()])
            query += f" WHERE {where_clause}"
        values = list(where.values())
        return query, values

    @staticmethod
    def select(table: str, columns: Optional[List[str]] = None, where: Optional[Dict[str, any]] = None,
               order_by: Optional[str] = None, limit: Optional[int] = None):

        columns_clause = ", ".join(columns) if columns else "*"
        query = f"SELECT {columns_clause} FROM {table}"
        if where:
            where_clause = "AND ".join([f"{key} = ?" for key in where.keys()])
            query += f" WHERE {where_clause}"

        if order_by:
            query += f" ORDER BY {order_by} DESC"
        if limit:
            query += f" LIMIT {limit}"
        values = [val for val in where.values()] if where else []

        return query, values