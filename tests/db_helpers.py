"""
# Example usage:

    async def main():
        db_url = "postgresql://user:password@localhost:5432/mydatabase"
        await create_db(db_url)
        exists = await db_exists(db_url)
        print(f"Database exists: {exists}")

"""

from urllib.parse import urlparse, urlunparse

import asyncpg


async def db_exists(db_url: str) -> bool:
    """Check if the database exists by attempting a connection.

    Returns True if connection succeeds; if it fails with an
    InvalidCatalogName error (or similar), returns False.
    """
    try:
        conn = await asyncpg.connect(db_url)
        await conn.close()
        return True
    except asyncpg.InvalidCatalogNameError:
        # This error indicates the database does not exist.
        return False
    except Exception as e:
        # You might want to re-raise or handle other errors differently.
        print(f"Unexpected error when checking DB existence: {e}")
        return False


async def create_db(db_url: str) -> None:
    """Create a PostgreSQL database if it doesn't exist.

    The function parses the provided db_url to extract the target
    database name, then connects to a default database (e.g., 'postgres')
    and issues a CREATE DATABASE command if needed.
    """
    parsed = urlparse(db_url)
    target_db = parsed.path.lstrip("/")

    # Build a new URL pointing to a default database for administrative actions.
    # For PostgreSQL, this is usually "postgres".
    default_db = "postgres"
    default_path = "/" + default_db
    admin_parsed = parsed._replace(path=default_path)
    admin_db_url = urlunparse(admin_parsed)

    # Check if the target database exists.
    if await db_exists(db_url):
        print(f"Database '{target_db}' already exists.")
        return

    print(f"Database '{target_db}' does not exist. Creating...")
    # Connect to the default database as a superuser
    # (make sure your credentials permit this).
    conn = await asyncpg.connect(admin_db_url)
    try:
        await conn.execute(f'CREATE DATABASE "{target_db}"')
        print(f"Database '{target_db}' created successfully.")
    finally:
        await conn.close()


async def drop_db(db_url: str) -> None:
    """Drop a PostgreSQL database if it exists.

    Connects to the default administrative database and attempts to drop
    the specified target database. In PostgreSQL 13 and later, this function
    uses the 'WITH (FORCE)' option to terminate active connections.

    Args:
        db_url (str): The connection URL of the target database to drop.
    """
    parsed = urlparse(db_url)
    target_db = parsed.path.lstrip("/")

    # Build a new URL pointing to the default administrative database.
    default_db = "postgres"
    admin_parsed = parsed._replace(path=f"/{default_db}")
    admin_db_url = urlunparse(admin_parsed)

    # Connect to the default administrative database.
    conn = await asyncpg.connect(admin_db_url)
    try:
        # Attempt to drop the target database with the FORCE option.
        drop_command = f'DROP DATABASE "{target_db}" WITH (FORCE)'
        await conn.execute(drop_command)
        print(f"Database '{target_db}' dropped successfully.")
    except asyncpg.InvalidCatalogNameError:
        print(f"Database '{target_db}' does not exist.")
    except asyncpg.PostgresError as e:
        print(f"Error dropping database '{target_db}': {e}")
    finally:
        await conn.close()
