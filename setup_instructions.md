# Setup Instructions for AICTE Activity & Points Management System

Follow these steps to set up and run the application locally.

## Prerequisite
1. Python 3.8 or higher installed
2. MySQL Server running locally on default port `3306`

## Step 1: Database Setup
1. Ensure your local MySQL server is running.
2. The application uses `$root` with NO password as default. If you have a different setup, edit the credentials in `config.py` under the `MYSQL_CONFIG` dictionary.
3. Open your terminal in this `py web internship` folder and log in to MySQL to run the schema file:
    ```bash
    mysql -u root -p < schema.sql
    ```
   *(Press Enter if there is no password)*.

This will construct the database (`aicte_db`), create tables, and populate dummy data for testing. 

*Sample Login Credentials included in `schema.sql`:*
- Admin: `admin` / `admin123`
- Club: `techclub` / `club123`
- Student: `rahul` / `student123`

## Step 2: Virtual Environment & Dependencies
1. Open a terminal in the project directory.
2. It is highly recommended to use a virtual environment:
    ```cmd
    python -m venv venv
    venv\Scripts\activate
    ```
3. Install dependencies from `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

## Step 3: Run the Flask Application
Start the back-end server by running:
```bash
python app.py
```

You should see output indicating that the application is running on `http://localhost:5000`.

## Step 4: Verification 
1. Open your web browser and go to `http://localhost:5000`
2. You'll see the landing page.
3. Login using one of the sample accounts.
4. If testing Student, browse events, register, and try opening the PDF report.
5. If testing Club, create a new event, manage attendees, and view the QR code generated.
6. The app supports Dark and Light mode which can be toggled using the ☀️/🌙 icon on the navbar.
