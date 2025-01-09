from langchain.sql_database import SQLDatabase
from typing import List, Dict, Any
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, user: str, password: str, host: str, database: str):
        self.connection_string = f"mysql+pymysql://{user}:{password}@{host}/{database}"
        self.db = self._initialize_database()
        self.engine = self._create_engine()

    def _initialize_database(self) -> SQLDatabase:
        """Initialize the SQLDatabase instance"""
        try:
            return SQLDatabase.from_uri(self.connection_string)
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise

    def _create_engine(self):
        """Create SQLAlchemy engine with connection pooling"""
        return create_engine(
            self.connection_string,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800
        )

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        connection = self.engine.connect()
        try:
            yield connection
        finally:
            connection.close()

    def get_tables(self) -> List[str]:
        """Get list of tables in the database"""
        try:
            with self.get_connection() as conn:
                result = conn.execute(text("SHOW TABLES"))
                return [row[0] for row in result]
        except Exception as e:
            logger.error(f"Error fetching tables: {str(e)}")
            raise

    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Get schema information for a specific table"""
        try:
            with self.get_connection() as conn:
                result = conn.execute(text(f"DESCRIBE {table_name}"))
                return [dict(row) for row in result]
        except Exception as e:
            logger.error(f"Error fetching schema for table {table_name}: {str(e)}")
            raise

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a raw SQL query"""
        try:
            with self.get_connection() as conn:
                result = conn.execute(text(query))
                return [dict(row) for row in result]
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise

    def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """Get statistics about a table"""
        try:
            with self.get_connection() as conn:
                row_count = conn.execute(
                    text(f"SELECT COUNT(*) FROM {table_name}")
                ).scalar()
                
                size_query = text("""
                    SELECT 
                        data_length + index_length as total_size,
                        index_length as index_size
                    FROM information_schema.TABLES
                    WHERE table_schema = :db_name
                    AND table_name = :table_name
                """)
                
                size_result = conn.execute(
                    size_query,
                    {"db_name": self.db.name, "table_name": table_name}
                ).first()

                return {
                    "row_count": row_count,
                    "total_size": size_result[0] if size_result else None,
                    "index_size": size_result[1] if size_result else None
                }
        except Exception as e:
            logger.error(f"Error fetching stats for table {table_name}: {str(e)}")
            raise

    def get_query_plan(self, query: str) -> str:
        """Get execution plan for a query"""
        try:
            with self.get_connection() as conn:
                result = conn.execute(text(f"EXPLAIN FORMAT=JSON {query}"))
                return result.scalar()
        except Exception as e:
            logger.error(f"Error getting query plan: {str(e)}")
            raise