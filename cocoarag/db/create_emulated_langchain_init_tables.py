import psycopg

# Database connection parameters
connection_params = {
    "dbname": "langchain",
    "user": "langchain",
    "password": "langchain",
    "host": "localhost",
    "port": "6024"
}


# turn on vectors stuff on psql
create_extension_sql = """
CREATE EXTENSION IF NOT EXISTS vector;
"""


create_collections_table_sql = """
CREATE TABLE public.langchain_pg_collection (
    "uuid" uuid NOT NULL,
    "user_id" uuid,
    "group_id" uuid,
    "name" varchar NOT NULL,
    cmetadata json NULL,
    CONSTRAINT langchain_pg_collection_name_key UNIQUE (name),
CONSTRAINT langchain_pg_collection_pkey PRIMARY KEY (uuid)
);
"""


# SQL command to create the table
create_embeddings_table_sql = """
    CREATE TABLE public.langchain_pg_embedding (
        id varchar NOT NULL,
        collection_id uuid NULL,
        embedding public.vector NULL,
        "document" varchar NULL,
        cmetadata jsonb NULL,
        CONSTRAINT langchain_pg_embedding_pkey PRIMARY KEY (id),
        CONSTRAINT langchain_pg_embedding_collection_id_fkey FOREIGN KEY (collection_id) REFERENCES public.langchain_pg_collection("uuid") ON DELETE CASCADE
    );
    CREATE INDEX ix_cmetadata_gin ON public.langchain_pg_embedding USING gin (cmetadata jsonb_path_ops);
    CREATE UNIQUE INDEX ix_langchain_pg_embedding_id ON public.langchain_pg_embedding USING btree (id);
"""


create_users_table_sql = """
    CREATE TABLE IF NOT EXISTS public.users (
    user_id UUID PRIMARY KEY, -- Primary key defined here
    group_id UUID,
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


def create_extension():
    try:
        # Connect to the PostgreSQL database
        with psycopg.connect(**connection_params) as conn:
            with conn.cursor() as cur:
                # Execute the SQL command to create the table
                cur.execute(create_extension_sql)
                conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")


def create_collection_table():
    try:
        # Connect to the PostgreSQL database
        with psycopg.connect(**connection_params) as conn:
            with conn.cursor() as cur:
                # Execute the SQL command to create the table
                cur.execute(create_collections_table_sql)
                conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")


def create_embedding_table():
    try:
        # Connect to the PostgreSQL database
        with psycopg.connect(**connection_params) as conn:
            with conn.cursor() as cur:
                # Execute the SQL command to create the table
                cur.execute(create_embeddings_table_sql)
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
    create_extension()
    print("Vector extension has been created successfully.")
    create_user_table_sql()
    print("Table 'user' created successfully.")
    create_collection_table()
    print("Table 'langchain_pg_collection' created successfully.")
    create_embedding_table()
    print("Table 'langchain_pg_embedding' created successfully.")
