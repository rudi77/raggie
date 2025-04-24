from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, select
from llama_index.core import SQLDatabase

def create_sql_database(db_url="sqlite:///:memory:"):
    """Create and initialize the SQL database."""
    engine = create_engine(db_url)
    metadata_obj = MetaData()
    
    # Create tables
    city_stats_table = Table(
        "city_stats",
        metadata_obj,
        Column("city_name", String(16), primary_key=True),
        Column("population", Integer),
        Column("country", String(16), nullable=False),
    )
    
    # Create all tables in the database
    metadata_obj.create_all(engine)
    
    # Create LlamaIndex SQLDatabase wrapper
    sql_database = SQLDatabase(engine, include_tables=["city_stats"])
    
    return sql_database, engine, metadata_obj

def insert_test_data(engine, city_stats_table):
    """Insert some test data into the database."""
    from sqlalchemy import insert
    
    rows = [
        {"city_name": "Toronto", "population": 2930000, "country": "Canada"},
        {"city_name": "Tokyo", "population": 13960000, "country": "Japan"},
        {"city_name": "Chicago", "population": 2679000, "country": "United States"},
        {"city_name": "Seoul", "population": 9776000, "country": "South Korea"},
    ]
    
    for row in rows:
        stmt = insert(city_stats_table).values(**row)
        with engine.begin() as connection:
            connection.execute(stmt) 