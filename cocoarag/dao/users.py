import psycopg
from psycopg.types.json import Jsonb

from cocoarag.dao.base import DAO


class AddUserDAO(DAO):
    def __call__(self,
                 user_id: str,
                 user_group: str,  # TODO: refactor it, user_group instead of group_id etc
                 username: str,
                 email: dict,
                 password: str,
                 metadata) -> None:
        """ Save new user into table 'users'."""
        insert_user_sql = """
        INSERT INTO public.users (user_id, user_group, username, email, password_hash, metadata)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        try:
            # Connect to the PostgreSQL database
            with psycopg.connect(**self.connection_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        insert_user_sql,
                        (
                            user_id,
                            user_group,
                            username,
                            email,
                            password,
                            Jsonb(metadata)
                        )
                    )
                    conn.commit()
        except Exception as e:
            print(f"Error saving User {username}: {e}")
            raise
