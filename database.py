from sqlmodel import create_engine, SQLModel, Session
# from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

# MySQL database configuration
# mysql_username = "root"
# mysql_password = "42xeZalB@"
# mysql_host = "localhost"
# mysql_port = 3306
# mysql_database = "inventory_management"

# # URL-encode the password
# encoded_password = quote_plus(mysql_password)

# # MySQL connection URL
# DB_url = f"mysql+pymysql://{mysql_username}:{encoded_password}@{mysql_host}:{mysql_port}/{mysql_database}"
# engine = create_engine(DB_url, echo=True)
# sqlite_file_name = "database.db"  # SQLite database file
# sqlite_url = f"sqlite:///{sqlite_file_name}"  # SQLite connection URL

# PostgreSQL database configuration
DATABASE_URL = os.getenv("DB_URL") 
engine = create_engine(DATABASE_URL, echo=True)  

# Function to create database tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Dependency to get a database session
def get_session():
    with Session(engine) as session:
        yield session