import os
import shutil
import sqlite3
import unittest

def find_duplicate_uniqnames(db_path):
    """
    Find all students who have multiple uniqnames in the system.
    
    Args:
        db_path (str): Path to the SQLite database
        
    Returns:
        list: List of tuples containing (name, list of uniqnames)
              Example: [("Alexandria Ocasio Cortez", ["acortez", "aocasiocortez"])]
    """
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    pass
    
    
def fix_uniqname(db_path, name, correct_uniqname):
    """
    Update the database to use the correct uniqname for a student and remove the incorrect one.
    
    Args:
        db_path (str): Path to the SQLite database
        name (str): Full name of the student
        correct_uniqname (str): The correct uniqname to keep
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    pass


def get_longest_uniqname_student(db_path):
    """
    Find the student with the longest uniqname in the database.
    In case of ties, return the alphabetically first student name.

    Args:
        db_path (str): Path to the SQLite database

    Returns:
        tuple: (student_name, uniqname, length)
        Example: ("Alexandria Ocasio Cortez", "aocasiocortez", 13)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    pass


class TestUniqnameCorrection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db = "test_directory.db"
        cls.backup_db = "backup_directory.db"

        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)
        if os.path.exists(cls.backup_db):
            os.remove(cls.backup_db)
        
        # Create test database
        conn = sqlite3.connect(cls.test_db)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )""")
        
        cursor.execute("""
        CREATE TABLE credentials (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            uniqname TEXT UNIQUE,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")
        
        cursor.execute("""
        CREATE TABLE enrollments (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            course_id TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")
        
        # Insert test data
        test_data = [
            (1, 'Alexandria Ocasio Cortez'),
            (2, 'Barbara Ericson'),
            (3, 'Barbara Smith'),
            (4, 'Alexandria Jones'),
            (5, 'Barbara Jones')
        ]
        cursor.executemany("INSERT INTO users (id, name) VALUES (?, ?)", test_data)
        
        # Insert credentials
        credentials_data = [
            (1, 'acortez'),
            (1, 'aocasiocortez'),
            (2, 'bericson'),
            (3, 'bsmith'),
            (4, 'ajones'),
            (5, 'bjones')
        ]
        cursor.executemany("INSERT INTO credentials (user_id, uniqname) VALUES (?, ?)", 
                          credentials_data)
        
        # Insert enrollments
        enrollments_data = [
            (1, 'SI206'),
            (2, 'SI206'),
            (3, 'SI206'),
            (4, 'SI206'),
            (5, 'SI206')
        ]
        cursor.executemany("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", 
                          enrollments_data)
        
        conn.commit()
        conn.close()
        
        # Create backup for each test
        shutil.copy2(cls.test_db, cls.backup_db)

    def setUp(self):
        # Restore from backup before each test
        shutil.copy2(self.backup_db, self.test_db)

    @classmethod
    def tearDownClass(cls):
        # Clean up databases
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)
        if os.path.exists(cls.backup_db):
            os.remove(cls.backup_db)

    def test_find_duplicate_uniqnames(self):
        duplicates = find_duplicate_uniqnames(self.test_db)
        
        # Check we found the right number of duplicates
        self.assertEqual(len(duplicates), 1)
        
        # Check the duplicate entry is correct
        name, uniqnames = duplicates[0]
        self.assertEqual(name, "Alexandria Ocasio Cortez")
        self.assertEqual(set(uniqnames), {"acortez", "aocasiocortez"})
        
        # Check that Barbara Ericson isn't in duplicates
        self.assertTrue(all(entry[0] != "Barbara Ericson" for entry in duplicates))

    def test_fix_uniqname(self):
        # Fix Maria's uniqname
        fix_uniqname(self.test_db, "Alexandria Ocasio Cortez", "aocasiocortez")
        
        # Connect and verify
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        # Check only one uniqname remains
        cursor.execute("""
            SELECT credentials.uniqname 
            FROM credentials 
            JOIN users ON credentials.user_id = users.id 
            WHERE users.name = 'Alexandria Ocasio Cortez'
        """)
        results = cursor.fetchall()
        
        # Verify only one uniqname exists now
        self.assertEqual(len(results), 1)
        
        # Verify it's the correct one
        self.assertEqual(results[0][0], "aocasiocortez")
        
        # Verify Barbara Ericson's data wasn't affected
        cursor.execute("""
            SELECT credentials.uniqname 
            FROM credentials 
            JOIN users ON credentials.user_id = users.id 
            WHERE users.name = 'Barbara Ericson'
        """)
        john_results = cursor.fetchall()
        self.assertEqual(len(john_results), 1)
        self.assertEqual(john_results[0][0], "bericson")
        
        conn.close()

    def test_get_longest_uniqname_student(self):
        result = get_longest_uniqname_student(self.test_db)

        # Check the result format
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)

        # Check the student with longest uniqname
        student_name, uniqname, length = result
        self.assertEqual(student_name, "Alexandria Ocasio Cortez")
        self.assertEqual(uniqname, "aocasiocortez")
        self.assertEqual(length, 13)

if __name__ == '__main__':
    unittest.main(verbosity=2)