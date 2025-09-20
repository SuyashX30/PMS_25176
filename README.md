# PMS_25176
Performance Management System (PMS)
This is a simple web-based Performance Management System (PMS) built with Python, Streamlit, and PostgreSQL. It's designed to help managers in a startup environment track their team's performance by setting goals, monitoring progress, providing feedback, and generating reports.

Core Features
Goal & Task Setting: Managers can set and view individual goals for their employees. Employees can view assigned goals and log tasks to achieve them, which are then subject to manager approval.

Progress Tracking: Both managers and employees can visualize the progress of tasks and goals. Managers have the exclusive ability to update a goal's status.

Feedback System:

Allows managers to provide written feedback on performance related to specific goals.

Includes automated feedback triggers (e.g., a congratulatory message when a goal is marked as 'Completed').

Reporting: Provides a clear historical view of an employee's performance, including all past and present goals, tasks, and feedback.

Business Insights: A manager-exclusive dashboard that provides high-level analytics, including total goals, goal status distribution, and top/lowest performers.

Tech Stack
Frontend: Streamlit

Backend: Python

Database: PostgreSQL

Database Connector: psycopg2-binary

Setup and Installation
Prerequisites
Python 3.8 or newer

A running instance of PostgreSQL

1. Get the Code
Download the following files and place them in the same project directory:

Frontend_pms.py

Backend_pms.py

Schema_pms.sql

requirements.txt

2. Install Dependencies
Navigate to your project directory in the terminal and run the following command to install the required Python libraries:

pip install -r requirements.txt

3. Configure the Database
A. Create the Database:

Connect to your PostgreSQL instance.

Create a new database for the application (e.g., pms_db).

B. Run the Schema Script:

Execute the contents of Schema_pms.sql on your newly created database. This will create the necessary tables, functions, and triggers.

C. Set Environment Variables:

The application connects to the database using environment variables for security. You must set these in your terminal before launching the app.

For Linux/macOS:

export DB_HOST="localhost"
export DB_NAME="pms_db"
export DB_USER="your_postgres_user"
export DB_PASSWORD="your_postgres_password"

For Windows (Command Prompt):

set DB_HOST="localhost"
set DB_NAME="pms_db"
set DB_USER="your_postgres_user"
set DB_PASSWORD="your_postgres_password"

Note: Replace "your_postgres_user" and "your_postgres_password" with your actual PostgreSQL credentials.

4. Run the Application
Once the setup is complete, run the Streamlit app from your terminal:

streamlit run Frontend_pms.py

Your web browser should open a new tab with the application running.

How to Use
Select a User: Use the sidebar to switch between different user profiles (Manager or Employee) to see how the application's functionality and views change.

Navigate Sections: Use the navigation dropdown in the sidebar to move between the different features of the PMS.

Interact: Follow the on-screen instructions to create goals, add tasks, update progress, and provide feedback.

File Structure
Frontend_pms.py: Contains all the Streamlit code for the user interface and application flow.

Backend_pms.py: Handles all database connections, queries, and business logic (CRUD operations, insights calculations).

Schema_pms.sql: The SQL script to initialize the database schema.

requirements.txt: A list of Python package dependencies.
