import csv
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Setup
engine = create_engine(
    os.getenv("DATABASE_URL"))  # database engine object from SQLAlchemy that manages connections to the database
# DATABASE_URL is an environment variable that indicates where the database lives
db = scoped_session(
    sessionmaker(bind=engine))  # create a 'scoped session' that ensures different users' interactions with the
# database are kept separate

# uncomment this to import everything from books.csv again
sys.exit()

# Drop tables
db.execute(
    """
    DROP TABLE IF EXISTS companies, users, reviews;
    """
)
db.commit()

# Create 3 tables - companies, users, reviews - if not exists
db.execute(
    """
    CREATE TABLE IF NOT EXISTS companies (
        company_id INTEGER PRIMARY KEY,
        name VARCHAR, 
        industry VARCHAR, 
        description VARCHAR, 
        year_founded VARCHAR, 
        employees VARCHAR, 
        state VARCHAR, 
        city VARCHAR, 
        area VARCHAR, 
        revenue VARCHAR, 
        expenses VARCHAR, 
        profit VARCHAR, 
        growth VARCHAR 
    )
    """
)
db.commit()

db.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        username VARCHAR NOT NULL PRIMARY KEY,
        password VARCHAR NOT NULL
    )
    """
)
db.commit()

db.execute(
    """
    CREATE TABLE IF NOT EXISTS reviews (
        username VARCHAR,
        company_id INTEGER,
        rating INTEGER NOT NULL,
        text VARCHAR NOT NULL,
        PRIMARY KEY (username, company_id),
        FOREIGN KEY (username) REFERENCES users (username),
        FOREIGN KEY (company_id) REFERENCES companies (company_id),
        CHECK (rating >= 1 AND rating <= 5)
    )
    """
)
db.commit()

# Import table from books.csv
f = open("companies.csv")
reader = csv.reader(f)
csv_headings = next(reader)  # skip the first heading row
print(csv_headings)
count = 0
for company_id, name, industry, description, year_founded, employees, state, city, area, revenue, expenses, profit, growth in reader:  # loop gives each column a name
    db.execute(
        "INSERT INTO companies (company_id, name, industry, description, year_founded, employees, state, city, area, revenue, expenses, profit, growth) \
         VALUES (:company_id, :name, :industry, :description, :year_founded, :employees, :state, :city, :area, :revenue, :expenses, :profit, :growth)", \
        {"company_id": company_id, "name": name, "industry": industry, "description": description,
         "year_founded": year_founded, "employees": employees, "state": state, "city": city, "area": area,
         "revenue": revenue, "expenses": expenses, "profit": profit, "growth": growth})
    print(f"Added company {count} with details {name} | {industry} | {year_founded}.")
    count += 1
try:
    db.commit()
except Exception as e:
    print(e)
