import csv
import io
import mysql.connector
from mysql.connector import Error as mysqlError


class CSVLogger:
    """
    A class to log data in memory as a CSV format.
    """

    def __init__(self, headers):
        """
        Initializes the CSVLogger object with headers and an in-memory CSV storage.

        :param headers: List containing the column headers for the CSV file.
        """
        self.headers = headers
        # Initialize an in-memory file-like string object
        self.memory_file = io.StringIO()
        # Write the header
        writer = csv.writer(self.memory_file)
        writer.writerow(self.headers)
        # Make sure to seek back to the start so future reads are from the beginning
        self.memory_file.seek(0)

    def log(self, **kwargs):
        """
        Logs data in memory. Log only one row at a time!

        :param kwargs: Keyword arguments where keys are column headers and values are data to be logged.
        """
        # Ensure all keys in kwargs are in the headers
        row = [kwargs.get(header, '') for header in self.headers]
        # Move to the end of the memory file before writing a new row
        self.memory_file.seek(0, io.SEEK_END)
        writer = csv.writer(self.memory_file)
        writer.writerow(row)
        # Seek back to the start for consistency
        self.memory_file.seek(0)

    def read_all(self):
        """
        Reads all data from the in-memory CSV storage.

        :return: A dictionary containing the data read, with headers as keys and lists of corresponding data as values.
        """
        # Initialize a dictionary with headers as keys and empty lists as values
        data = {header: [] for header in self.headers}
        # Read the in-memory file from the beginning
        self.memory_file.seek(0)
        reader = csv.DictReader(self.memory_file)
        for row in reader:
            for header in self.headers:
                data[header].append(row.get(header, ''))
        # After reading, seek back to the end to allow appending new rows correctly
        self.memory_file.seek(0, io.SEEK_END)
        return data


class MySQLLogger:
    """
    A class designed to facilitate logging and interacting with a MySQL database. It enables the creation, deletion,
    and querying of tables, as well as logging and reading data from them.
    """

    def __init__(self, host, user, password, database):
        """
        Initializes the MySQLLogger object with the details required to connect to a MySQL database, such as host,
        user, password, and the specific database to use. Upon initialization, it attempts to establish a connection
        to the specified database and updates the internal mapping of tables and their columns.

        :param host: The host name or IP address of the MySQL server.
        :param user: The username to use for authentication with the MySQL server.
        :param password: The password to use for authentication with the MySQL server.
        :param database: The name of the database to connect to.
        """
        self.db_config = {'host': host, 'user': user, 'password': password, 'database':database}
        self.database = database
        self.tables_and_headers = {}  # {'table1': ['header1', 'header2'], 'table2': ['header1', 'header2']}
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            if not self.connection.is_connected():
                raise ConnectionError(f"Error while connecting to MySQL. Try again.")
            self.update_tables_and_headers_vars()
        except mysqlError as e:
            self.connection = None
            raise ConnectionError(f"Error while connecting to MySQL: {e}")

    def close_connection(self):
        """
        Closes the existing database connection. If the connection is already closed or null, it performs no operation.
        """
        try:
            if self.connection.is_connected():
                self.connection.close()
            self.connection = None
        except Exception:
            self.connection = None

    def get_tables_and_headers(self):
        """
        Returns the current mapping of table names to their columns (headers) as a dictionary.

        :return: A dictionary where keys are table names and values are lists of column names (headers) for those tables.
        """
        return self.tables_and_headers

    def connection_available(self):
        """
        Checks if the database connection is currently established and returns True if so, and False otherwise.

        :return: True if the database connection is available, False otherwise.
        """
        try:
            return True if self.connection.is_connected() else False
        except Exception:
            return False

    def _execute_query(self, query, params=None, fetch=False):
        """
        A private method to execute a SQL query on the connected database. It supports executing queries with or
        without parameters and can optionally fetch and return query results. This method is used internally to
        abstract and handle SQL execution, including committing transactions and fetching results.

        :param query: The SQL query to be executed.
        :param params: Optional parameters to be included with the query.
        :param fetch: Whether to fetch and return the results of the query.
        :return: The results of the query if fetch is True, otherwise None.
        """
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            if fetch:
                result = cursor.fetchall()
                return result
            self.connection.commit()
        except mysqlError as e:
            raise SyntaxError(f"Resulted error: {e} \nWhile executing query: {query}")
        finally:
            cursor.close()

    def update_tables_and_headers_vars(self):
        """
        Queries the database for all tables and their columns within the current schema and updates the internal
        mapping to reflect the current database structure. This method is useful for synchronizing the class's
        understanding of the database schema with the actual database.
        """
        query = f"""SELECT table_name, column_name
                FROM information_schema.columns
                WHERE table_schema = '{self.database}'
                ORDER BY table_name, ordinal_position;"""
        results = self._execute_query(query, fetch=True)
        tables_columns_dict = {}
        for row in results:
            table_name, column_name = row
            if table_name not in tables_columns_dict:
                tables_columns_dict[table_name] = []
            tables_columns_dict[table_name].append(column_name)
        self.tables_and_headers = tables_columns_dict

    def ensure_table_exists(self, table_name, headers: dict):
        """
        Checks if a table exists in the database, and if not, creates it using the specified table name and column
        definitions provided in the headers dictionary. This method ensures that the application can operate with the
        required tables without manual database setup.

        :param table_name: The name of the table to ensure exists or create.
        :param headers: A dictionary where keys are column names and values are data types for the columns.
        """
        if not self.connection_available():
            raise ConnectionError("Connection not available")
        table_name = str(table_name).replace(" ", "_")
        columns_definitions = ', '.join([f"`{column}` {data_type}" for column, data_type in headers.items()])
        create_table_query = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns_definitions});"
        self._execute_query(create_table_query,)
        self.update_tables_and_headers_vars()

    def remove_table(self, table_name):
        """
        Removes a table from the database if it exists. This operation is irreversible and should be used with caution.

        :param table_name: The name of the table to be removed.
        """
        if not self.connection_available():
            raise ConnectionError("Connection not available")
        query = f"""DROP TABLE IF EXISTS {table_name};"""
        self._execute_query(query)
        self.update_tables_and_headers_vars()

    def log(self, table_name, data):
        """
        Logs data to the specified table. The data can be in the form of a single row as a list, multiple rows as a list of lists,
        a single row as a dictionary of key-value pairs, or multiple rows as a dictionary of key-list pairs.

        :param table_name: The name of the table to log data to.
        :param data: The data to log.
        """
        if not self.connection_available():
            raise ConnectionError("Connection not available")

        headers = self.tables_and_headers[table_name]

        if isinstance(data, list):
            if not data:  # Check if the list is empty
                raise ValueError("Data is empty.")
            if isinstance(data[0], list):  # Multiple rows as list of lists
                rows = data
            else:  # Single row as list of values
                rows = [data]
        elif isinstance(data, dict):
            if all(isinstance(value, list) for value in data.values()):  # Multiple rows as dict of lists
                lengths = [len(values) for values in data.values()]
                if len(set(lengths)) > 1:
                    raise ValueError("All columns must have the same number of entries.")
                rows = list(zip(*[data.get(header, []) for header in headers]))
            else:  # Single row as dict
                single_row = [data.get(header) for header in headers]
                rows = [single_row]
        else:
            raise TypeError("Invalid data type. Data should be either a list or a dict.")

        columns = ', '.join(headers)
        placeholders = ', '.join(['%s'] * len(headers))
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"

        cursor = self.connection.cursor()
        try:
            cursor.executemany(insert_query, rows)
            self.connection.commit()
        except Exception as e:  # Changed from mysqlError to a more general exception handling
            self.connection.rollback()
            raise e
        finally:
            cursor.close()

    def legacy_log(self, table_name, data: dict or list):
        """
        Logs data to the specified table. The data can be provided as a dictionary, where keys correspond to column
        names, or as a list, where the order of values must match the order of the columns in the table. This method
        abstracts the insertion process, making it easy to log data to the database.

        :param table_name: The name of the table to log data to.
        :param data: The data to log, either as a dictionary with column names as keys or a list of values in the order
        of the table columns.
        """
        if not self.connection_available():
            raise ConnectionError("Connection not available")

        headers = self.tables_and_headers[table_name]
        if type(data) == list:
            if len(data) != len(headers):
                raise ValueError(f"Passed data doesn't match with table's headers! Table '{table_name}' headers are:\n{headers}")
            else:
                log_data = data
        elif type(data) == dict:
            log_data = [value for key, value in data.items()]
            if len(log_data) != len(headers):
                raise ValueError(f"Passed data doesn't match with table's headers! Table '{table_name}' headers are:\n{headers}")
        else:
            raise TypeError("Invalid type for data. It should be list or dict.")

        columns = ', '.join(headers)
        placeholders = ', '.join(['%s'] * len(log_data))
        values = tuple(log_data)
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"
        self._execute_query(insert_query, params=values, fetch=False)

    def read_from(self, table_name):
        """
        Reads and returns all data from the specified table. The data is returned as a dictionary where each key is a
        column header and the corresponding value is a list of data entries for that column. This method allows for
        easy retrieval of tabular data from the database.

        :param table_name: The name of the table from which to read data.
        :return: A dictionary containing the data read from the table, with column headers as keys and lists of data as values.
        """
        if not self.connection_available():
            raise ConnectionError("Connection not available")
        if table_name not in self.tables_and_headers.keys():
            raise KeyError(f"Table '{table_name}' not found from database. Try to refresh database connection.")
        headers = self.tables_and_headers[table_name]
        select_query = f"SELECT {', '.join(headers)} FROM {table_name};"
        results = self._execute_query(select_query, fetch=True)
        if results is None:
            return {}
        # Initialize a dictionary with headers as keys and empty lists as values
        data = {header: [] for header in headers}
        for row in results:
            for header, value in zip(headers, row):
                data[header].append(value)
        return data

    def find_rows_by_value(self, table_name, column_name, search_value):
        """
        Searches for rows in the database where the specified column matches the provided search value.

        :param table_name: The name of the table to search in.
        :param column_name: The name of the column to search.
        :param search_value: The value to search for in the specified column.
        :return: A list of matching rows, or None if there are no matches.
        """
        if not self.connection_available():
            raise ConnectionError("Connection not available")
        if table_name not in self.tables_and_headers.keys():
            raise KeyError(f"Table '{table_name}' not found from database. Try to refresh database connection.")
        query = f"""
        SELECT * FROM `{table_name}`
        WHERE `{column_name}` = %s;
        """
        results = self._execute_query(query, params=(search_value,), fetch=True)
        # Check if the query returned any results
        if results:
            return results
        else:
            return None

    def pop_rows_by_value(self, table_name, column_name, search_value):
        """
        'Pops' (selects and deletes) rows in the specified table where the specified column matches
        the provided search value. Returns the rows that were deleted.

        :param table_name: The name of the table to delete rows from.
        :param column_name: The name of the column to search for the value.
        :param search_value: The value to search for in the specified column.
        :return: The rows that were deleted, if any.
        """
        rows_to_delete = self.find_rows_by_value(table_name, column_name, search_value)
        if rows_to_delete:
            delete_query = f"DELETE FROM `{table_name}` WHERE `{column_name}` = %s;"
            self._execute_query(delete_query, params=(search_value,), fetch=False)
            return rows_to_delete
        else:
            return []
