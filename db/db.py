import psycopg2

# Connection string (Neon URI)
DATABASE_URL = "postgresql://neondb_owner:npg_C35PwqnEgdaL@ep-rough-sun-a1ncs8pp-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_conn():
    """Return a PostgreSQL connection using URI."""
    return psycopg2.connect(DATABASE_URL)