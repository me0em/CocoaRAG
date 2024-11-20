import psycopg

# Database connection parameters
connection_params = {
    "dbname": "langchain",
    "user": "langchain",
    "password": "langchain",
    "host": "localhost",
    "port": "6024",
}


create_documents_table_sql = """
CREATE TABLE public.documents (
    "document_id" UUID PRIMARY KEY UNIQUE NOT NULL,
    "user_id" uuid,
    "user_group" uuid,
    "name" varchar NOT NULL,
    "content" bytea,
    cmetadata json
);
"""

create_users_table_sql = """
    CREATE TABLE IF NOT EXISTS public.users (
    user_id UUID PRIMARY KEY, -- Primary key defined here
    user_group UUID,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    metadata JSONB
);

-- Adding the foreign key constraint to reference the same table, if needed
ALTER TABLE IF EXISTS public.users
ADD CONSTRAINT langchain_pg_collection_user_id_fkey
FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;
"""

create_conversations_table_sql = """
    CREATE TABLE IF NOT EXISTS public.conversations (
    conversation_id UUID PRIMARY KEY UNIQUE NOT NULL,
    user_id UUID,
    content JSONB,
    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
        REFERENCES public.users(user_id)
        ON DELETE CASCADE
);
"""


def create_documents():
    try:
        # Connect to the PostgreSQL database
        with psycopg.connect(**connection_params) as conn:
            with conn.cursor() as cur:
                cur.execute(create_documents_table_sql)
                conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")


def create_conversations():
    try:
        # Connect to the PostgreSQL database
        with psycopg.connect(**connection_params) as conn:
            with conn.cursor() as cur:
                # Execute the SQL command to create the table
                cur.execute(create_conversations_table_sql)
                conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")


def create_user_table_sql():
    try:
        # Connect to the PostgreSQL database
        with psycopg.connect(**connection_params) as conn:
            with conn.cursor() as cur:
                # Execute the SQL command to create the table
                cur.execute(create_users_table_sql)
                conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")


if __name__ == "__main__":
    create_documents()
    print("Table 'documents' created successfully.")
    create_user_table_sql()
    print("Table 'user' created successfully.")
    create_conversations()
    print("Table 'conversations' created successfully.")
