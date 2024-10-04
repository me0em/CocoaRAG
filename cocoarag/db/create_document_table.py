import psycopg

# Database connection parameters
connection_params = {
    "dbname": "langchain",
    "user": "langchain",
    "password": "langchain",
    "host": "localhost",
    "port": "6024"
}

# SQL command to create the table
create_table_sql = """
CREATE TABLE IF NOT EXISTS document (
    id SERIAL PRIMARY KEY,
    collection_id VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    document_metadata TEXT
);
"""


def create_table():
    try:
        # Connect to the PostgreSQL database
        with psycopg.connect(**connection_params) as conn:
            with conn.cursor() as cur:
                # Execute the SQL command to create the table
                cur.execute(create_table_sql)
                conn.commit()
                print("Table 'document' created successfully.")
    except Exception as e:
        print(f"Error creating table: {e}")


if __name__ == "__main__":
    create_table()
