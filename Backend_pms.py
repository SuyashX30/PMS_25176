import psycopg2
import os
from datetime import date

# --- Database Connection ---
def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            database=os.environ.get("DB_NAME", "PMS"),
            user=os.environ.get("DB_USER", "postgres"),
            password=os.environ.get("DB_PASSWORD", "Suy23")
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to the database: {e}")
        return None

def setup_database():
    """Sets up the necessary tables in the database if they don't exist."""
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    manager_id INTEGER REFERENCES employees(id)
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS goals (
                    id SERIAL PRIMARY KEY,
                    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
                    description TEXT NOT NULL,
                    due_date DATE NOT NULL,
                    status VARCHAR(50) NOT NULL CHECK (status IN ('Draft', 'In Progress', 'Completed', 'Cancelled'))
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    goal_id INTEGER REFERENCES goals(id) ON DELETE CASCADE,
                    description TEXT NOT NULL,
                    is_approved BOOLEAN DEFAULT FALSE
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    goal_id INTEGER REFERENCES goals(id) ON DELETE CASCADE,
                    manager_id INTEGER REFERENCES employees(id),
                    feedback_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            # --- Automated Feedback Trigger ---
            cur.execute("""
                CREATE OR REPLACE FUNCTION goal_completed_feedback()
                RETURNS TRIGGER AS $$
                BEGIN
                    IF NEW.status = 'Completed' AND OLD.status != 'Completed' THEN
                        INSERT INTO feedback (goal_id, manager_id, feedback_text, created_at)
                        VALUES (NEW.id, (SELECT manager_id FROM employees WHERE id = NEW.employee_id), 'Great job on completing this goal!', NOW());
                    END IF;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;

                DROP TRIGGER IF EXISTS goal_completed_trigger ON goals;
                CREATE TRIGGER goal_completed_trigger
                AFTER UPDATE ON goals
                FOR EACH ROW
                EXECUTE FUNCTION goal_completed_feedback();
            """)
        conn.commit()
        conn.close()

# --- CRUD Operations for Employees ---
def create_employee(name, manager_id=None):
    """Creates a new employee."""
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO employees (name, manager_id) VALUES (%s, %s)",
                (name, manager_id)
            )
        conn.commit()
        conn.close()

def get_employees():
    """Retrieves all employees."""
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM employees ORDER BY name")
            employees = cur.fetchall()
        conn.close()
        return employees
    return []

# --- CRUD Operations for Goals ---
# Create
def create_goal(employee_id, description, due_date):
    """Allows a manager to create a new goal for an employee."""
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO goals (employee_id, description, due_date, status) VALUES (%s, %s, %s, 'Draft')",
                (employee_id, description, due_date)
            )
        conn.commit()
        conn.close()

# Read
def get_goals_for_employee(employee_id):
    """Retrieves all goals for a specific employee."""
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, description, due_date, status FROM goals WHERE employee_id = %s ORDER BY due_date DESC",
                (employee_id,)
            )
            goals = cur.fetchall()
        conn.close()
        return goals
    return []

# Update
def update_goal_status(goal_id, status):
    """Allows a manager to update the status of a goal."""
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE goals SET status = %s WHERE id = %s",
                (status, goal_id)
            )
        conn.commit()
        conn.close()

# Delete
def delete_goal(goal_id):
    """Allows a manager to delete a goal."""
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM goals WHERE id = %s", (goal_id,))
        conn.commit()
        conn.close()

# --- CRUD Operations for Tasks ---
# Create
def create_task(goal_id, description):
    """Allows an employee to log a task for a goal."""
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tasks (goal_id, description) VALUES (%s, %s)",
                (goal_id, description)
            )
        conn.commit()
        conn.close()

# Read
def get_tasks_for_goal(goal_id):
    """Retrieves all tasks for a specific goal."""
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, description, is_approved FROM tasks WHERE goal_id = %s ORDER BY id",
                (goal_id,)
            )
            tasks = cur.fetchall()
        conn.close()
        return tasks
    return []

# Update
def approve_task(task_id):
    """Allows a manager to approve a task."""
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE tasks SET is_approved = TRUE WHERE id = %s",
                (task_id,)
            )
        conn.commit()
        conn.close()

# Delete
def delete_task(task_id):
    """Allows a manager or employee to delete a task."""
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        conn.commit()
        conn.close()

# --- CRUD Operations for Feedback ---
# Create
def create_feedback(goal_id, manager_id, feedback_text):
    """Allows a manager to provide written feedback on a goal."""
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO feedback (goal_id, manager_id, feedback_text) VALUES (%s, %s, %s)",
                (goal_id, manager_id, feedback_text)
            )
        conn.commit()
        conn.close()

# Read
def get_feedback_for_goal(goal_id):
    """Retrieves all feedback for a specific goal."""
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT f.feedback_text, e.name, f.created_at FROM feedback f JOIN employees e ON f.manager_id = e.id WHERE f.goal_id = %s ORDER BY f.created_at DESC",
                (goal_id,)
            )
            feedback = cur.fetchall()
        conn.close()
        return feedback
    return []
    
# --- Business Insights ---
def get_performance_insights():
    """Gathers various performance metrics from the database."""
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            # Total goals
            cur.execute("SELECT COUNT(*) FROM goals;")
            total_goals = cur.fetchone()[0]

            # Goals by status
            cur.execute("SELECT status, COUNT(*) FROM goals GROUP BY status;")
            goals_by_status = cur.fetchall()

            # Average goals per employee
            cur.execute("""
                SELECT AVG(goal_count) FROM (
                    SELECT employee_id, COUNT(id) AS goal_count
                    FROM goals
                    GROUP BY employee_id
                ) AS employee_goals;
            """)
            avg_goals = cur.fetchone()[0]
            
            # Employee with most completed goals
            cur.execute("""
                SELECT e.name, COUNT(g.id)
                FROM employees e
                JOIN goals g ON e.id = g.employee_id
                WHERE g.status = 'Completed'
                GROUP BY e.name
                ORDER BY COUNT(g.id) DESC
                LIMIT 1;
            """)
            top_performer = cur.fetchone()

            # Employee with least completed goals
            cur.execute("""
                SELECT e.name, COUNT(g.id)
                FROM employees e
                LEFT JOIN goals g ON e.id = g.employee_id AND g.status = 'Completed'
                GROUP BY e.name
                ORDER BY COUNT(g.id) ASC
                LIMIT 1;
            """)
            lowest_performer = cur.fetchone()

        conn.close()
        return {
            "total_goals": total_goals,
            "goals_by_status": dict(goals_by_status),
            "average_goals_per_employee": f"{avg_goals:.2f}" if avg_goals else 0,
            "top_performer": top_performer[0] if top_performer else "N/A",
            "lowest_performer": lowest_performer[0] if lowest_performer else "N/A"
        }
    return {}

# --- Initial Data Seeding ---
def seed_data():
    """Populates the database with initial sample data."""
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM employees")
            if cur.fetchone()[0] == 0:
                # Managers
                cur.execute("INSERT INTO employees (name) VALUES ('Alice Manager') RETURNING id;")
                alice_id = cur.fetchone()[0]
                # Employees
                cur.execute("INSERT INTO employees (name, manager_id) VALUES ('Bob Smith', %s)", (alice_id,))
                cur.execute("INSERT INTO employees (name, manager_id) VALUES ('Charlie Brown', %s)", (alice_id,))
        conn.commit()
        conn.close()
