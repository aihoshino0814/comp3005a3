import psycopg2
from psycopg2 import sql

DB_CONFIG = {
    "host":     "127.0.0.1",
    "port":     5000,
    "dbname":   "test_db",
    "user":     "postgres",
    "password": "snowpea1234",
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def getAllStudents():
    query = """
        SELECT student_id, first_name, last_name, email, enrollment_date
        FROM students
        ORDER BY student_id;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

    if not rows:
        print("No students found.")
        return


    print(f"{'ID':<5}{'First Name':<15}{'Last Name':<15}{'Email':<30}{'Enrollment Date'}")
    print("-" * 85)
    for row in rows:
        student_id, first_name, last_name, email, enrollment_date = row
        print(f"{student_id:<5}{first_name:<15}{last_name:<15}{email:<30}{enrollment_date}")
    print(f"\nTotal students: {len(rows)}")


def addStudent(first_name, last_name, email, enrollment_date):
    query = """
        INSERT INTO students (first_name, last_name, email, enrollment_date)
        VALUES (%s, %s, %s, %s)
        RETURNING student_id;
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (first_name, last_name, email, enrollment_date))
                new_id = cur.fetchone()[0]
                conn.commit()
        print(f"Student added successfully with ID {new_id}.")
    except psycopg2.errors.UniqueViolation:
        print(f"Error: a student with email '{email}' already exists.")
    except Exception as e:
        print(f"Error adding student: {e}")


def updateStudentEmail(student_id, new_email):
    query = """
        UPDATE students
        SET email = %s
        WHERE student_id = %s;
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (new_email, student_id))
                affected = cur.rowcount
                conn.commit()
        if affected == 0:
            print(f"No student found with ID {student_id}.")
        else:
            print(f"Email updated for student ID {student_id}.")
    except psycopg2.errors.UniqueViolation:
        print(f"Error: the email '{new_email}' is already used by another student.")
    except Exception as e:
        print(f"Error updating email: {e}")


def deleteStudent(student_id):
    query = "DELETE FROM students WHERE student_id = %s;"
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (student_id,))
                affected = cur.rowcount
                conn.commit()
        if affected == 0:
            print(f"No student found with ID {student_id}.")
        else:
            print(f"Student with ID {student_id} deleted.")
    except Exception as e:
        print(f"Error deleting student: {e}")

def main():
    menu = """
===== Student Database Menu =====
1. Show all students
2. Add a student
3. Update a student's email
4. Delete a student
5. Exit
Choose an option (1-5): """

    while True:
        choice = input(menu).strip()

        if choice == "1":
            getAllStudents()

        elif choice == "2":
            first = input("First name: ").strip()
            last  = input("Last name: ").strip()
            email = input("Email: ").strip()
            date  = input("Enrollment date (YYYY-MM-DD, leave empty for NULL): ").strip() or None
            addStudent(first, last, email, date)

        elif choice == "3":
            try:
                sid = int(input("Student ID: ").strip())
            except ValueError:
                print("Student ID must be an integer.")
                continue
            new_email = input("New email: ").strip()
            updateStudentEmail(sid, new_email)

        elif choice == "4":
            try:
                sid = int(input("Student ID: ").strip())
            except ValueError:
                print("Student ID must be an integer.")
                continue
            confirm = input(f"Delete student {sid}? (Y/N): ").strip().lower()
            if confirm == "y":
                deleteStudent(sid)

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid option, please try again.")


if __name__ == "__main__":
    main()