import sqlite3
import hashlib
import os
from datetime import datetime

class Database:
    def __init__(self, db_name="university_data.db"):
        """Initialize database connection"""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Create required tables if they don't exist"""
        # Create students table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            pronouns TEXT,
            dob TEXT NOT NULL,
            home_address TEXT NOT NULL,
            term_address TEXT,
            emergency_name TEXT NOT NULL,
            emergency_number TEXT NOT NULL,
            course TEXT NOT NULL,
            registration_date TEXT NOT NULL
        )
        ''')

        # Create lecturers table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS lecturers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        ''')
        
        # Check if default lecturer exists, if not create one
        self.cursor.execute("SELECT * FROM lecturers WHERE username = 'admin'")
        if not self.cursor.fetchone():
            hashed_password = self._hash_password('admin123')
            self.cursor.execute("INSERT INTO lecturers (username, password) VALUES (?, ?)", 
                               ('admin', hashed_password))
        
        self.conn.commit()

    def _hash_password(self, password):
        """Hash a password for secure storage"""
        salt = os.urandom(32)  # 32 bytes of random salt
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt.hex() + ':' + key.hex()

    def _verify_password(self, stored_password, provided_password):
        """Verify a stored password against one provided by user"""
        salt_hex, key_hex = stored_password.split(':')
        salt = bytes.fromhex(salt_hex)
        stored_key = bytes.fromhex(key_hex)
        new_key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
        return new_key == stored_key

    def register_student(self, username, password, name, pronouns, dob, home_address,
                        term_address, emergency_name, emergency_number, course):
        """Register a new student"""
        try:
            hashed_password = self._hash_password(password)
            registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute('''
            INSERT INTO students (username, password, name, pronouns, dob, home_address, 
                                term_address, emergency_name, emergency_number, course, registration_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, hashed_password, name, pronouns, dob, home_address, term_address, 
                 emergency_name, emergency_number, course, registration_date))
            
            self.conn.commit()
            return True, "Registration successful!"
        except sqlite3.IntegrityError:
            return False, "Username already exists. Please choose a different one."
        except Exception as e:
            return False, f"Error: {str(e)}"

    def login_student(self, username, password):
        """Authenticate a student"""
        self.cursor.execute("SELECT id, password FROM students WHERE username = ?", (username,))
        result = self.cursor.fetchone()
        
        if not result:
            return False, "Invalid username or password"
        
        student_id, stored_password = result
        if self._verify_password(stored_password, password):
            return True, student_id
        else:
            return False, "Invalid username or password"

    def login_lecturer(self, username, password):
        """Authenticate a lecturer"""
        self.cursor.execute("SELECT id, password FROM lecturers WHERE username = ?", (username,))
        result = self.cursor.fetchone()
        
        if not result:
            return False, "Invalid username or password"
        
        lecturer_id, stored_password = result
        if self._verify_password(stored_password, password):
            return True, lecturer_id
        else:
            return False, "Invalid username or password"

    def get_student_data(self, student_id):
        """Get data for a specific student"""
        self.cursor.execute('''
        SELECT username, name, pronouns, dob, home_address, term_address, 
               emergency_name, emergency_number, course
        FROM students WHERE id = ?
        ''', (student_id,))
        
        result = self.cursor.fetchone()
        if result:
            return {
                'username': result[0],
                'name': result[1],
                'pronouns': result[2],
                'dob': result[3],
                'home_address': result[4],
                'term_address': result[5],
                'emergency_name': result[6],
                'emergency_number': result[7],
                'course': result[8]
            }
        return None

    def get_all_students(self):
        """Get data for all students (for lecturer view)"""
        self.cursor.execute('''
        SELECT id, username, name, pronouns, dob, home_address, term_address, 
               emergency_name, emergency_number, course
        FROM students
        ''')
        
        students = []
        for row in self.cursor.fetchall():
            students.append({
                'id': row[0],
                'username': row[1],
                'name': row[2],
                'pronouns': row[3],
                'dob': row[4],
                'home_address': row[5],
                'term_address': row[6],
                'emergency_name': row[7],
                'emergency_number': row[8],
                'course': row[9]
            })
        return students

    def update_student_data(self, student_id, data):
        """Update student data"""
        try:
            self.cursor.execute('''
            UPDATE students SET
                name = ?,
                pronouns = ?,
                dob = ?,
                home_address = ?,
                term_address = ?,
                emergency_name = ?,
                emergency_number = ?,
                course = ?
            WHERE id = ?
            ''', (
                data['name'],
                data['pronouns'],
                data['dob'],
                data['home_address'],
                data['term_address'],
                data['emergency_name'],
                data['emergency_number'],
                data['course'],
                student_id
            ))
            
            self.conn.commit()
            return True, "Data updated successfully!"
        except Exception as e:
            return False, f"Error updating data: {str(e)}"

    def close(self):
        """Close the database connection"""
        self.conn.close()