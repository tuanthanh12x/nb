import json
import psycopg2

def load_config(path="config.json"):
    """Load DB config from JSON file."""
    with open(path, "r") as f:
        return json.load(f)
# Connection string (Neon URI)

def get_conn():
    """Return a PostgreSQL connection using config.json"""
    config = load_config()

    conn = psycopg2.connect(
        host=config.get("host"),
        port=config.get("port"),
        dbname=config.get("dbname"),
        user=config.get("username"),
        password=config.get("password"),
        sslmode=config.get("sslmode")
    )
    return conn