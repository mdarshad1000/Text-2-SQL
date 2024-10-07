import psycopg2
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

class DatabaseExecutor:
    
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        """Establish Database Connection"""
        if self.connection is None or self.connection.closed:
            try:
                self.connection = psycopg2.connect(
                    host=os.getenv('HOST'),
                    port=os.getenv('PORT'),
                    database=os.getenv('POSTGRES_DB'),
                    user=os.getenv('POSTGRES_USER'),
                    password=os.getenv('POSTGRES_PASSWORD')
                )
                self.cursor = self.connection.cursor()
            except psycopg2.Error as e:
                raise ConnectionError(f"Failed to connect to database: {str(e)}")

    def disconnect(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def execute_query(self, query: str):
        """Executes SQL query with error handling."""
        try:
            if self.connection is None or self.connection.closed or self.cursor is None or self.cursor.closed:
                self.connect()
            self.cursor.execute(query)
            cols = [desc[0] for desc in self.cursor.description]
            rows = self.cursor.fetchall()
            df = pd.DataFrame(rows, columns=cols)
            return df
        except Exception as e:
            print(f"Error executing query: {str(e)}")
            return pd.DataFrame()
        finally:
            if self.cursor is not None:
                self.disconnect()
   
    def get_schema_info(self):
        """
        Retrieve database schema information as a pandas DataFrame and a formatted string.
        
        Returns:
            A tuple containing a pandas DataFrame and a formatted string with table and column information.
        """
        schema_query = """
        SELECT 
            table_name, 
            column_name, 
            data_type
        FROM 
            information_schema.columns
        WHERE 
            table_schema = 'public'
        ORDER BY 
            table_name, ordinal_position;
        """
        
        try:
            if not self.connection or self.connection.closed:
                self.connect()
                
            self.cursor.execute(schema_query)
            rows = self.cursor.fetchall()
            # Convert the fetched rows into a pandas DataFrame
            df = pd.DataFrame(rows, columns=['Table Name', 'Column Name', 'Data Type'])
            # Create a formatted string from the fetched rows
            schema_info_str = "\n".join([f"Table: {row[0]}, Column: {row[1]}, Type: {row[2]}" for row in rows])
            return df, schema_info_str  # Return both DataFrame and the formatted string
        except Exception as e:
            print(f"Error retrieving schema: {str(e)}")
            return pd.DataFrame(), ""  # Return an empty DataFrame and string in case of an error