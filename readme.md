# Running the project

The project runs using the flask framework for python and Postgres database, the project requires the following packages installed.

 1. Flask
 2. SQLAlchemy
 3. wtforms
 4. flask_login
 5. dotenv
 6. psycopg2 -- python's Postgres adapter

## Procedure

clone the repository from GitHub (https://github.com/rishabhrao076/dbo-project-python) or download it locally.

Download and restore the updated database. Run The postgres database.

Create a copy of the .env.example file called .env file and fill the relevant fields as per the requirements
the env file contains variables such as database host and port and app key which the application requires to connect to the database and run normally

open the commandline in the root folder and type **python app.py** to run the flask server