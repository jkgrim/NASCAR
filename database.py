import sqlite3
import bcrypt

from typing import List
from user import User
from competency import Competency
from assessment import Assessment
from result import Result
from singleton import Singleton

class Database(Singleton):

    def __init__(self, db_filename):
        self.connection = sqlite3.connect(db_filename)

    def authenticate(self, email: str, password: str) -> User:
        result = list(self.connection.cursor().execute('SELECT * from Users WHERE email = ?', (email,)))
        if len(result) != 1:
            raise Exception('User does not exist')
        row = result[0]
        hashed = bcrypt.hashpw(password.encode(), row[6])
        if hashed != row[5]:
            raise Exception('Authentication error')
        else:
            return self.get_user(row[0])

    def create_user(self, first_name, last_name, phone, email, password, date_created, hire_date, user_type):
        result = list(self.connection.cursor().execute('SELECT * FROM Users WHERE email = ?', (email,)))
        if len(result) != 0:
            raise Exception('A user with that email already exists')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        active = 1
        query = 'INSERT INTO Users (first_name, last_name, phone, email, password, salt, active, date_created, hire_date, user_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        values = (first_name, last_name, phone, email, hashed, salt, active, date_created, hire_date, user_type)
        cursor = self.connection.cursor()
        cursor.execute(query, values)
        self.connection.commit()
        return User(cursor.lastrowid, *values)
        
    def create_competency(self, name, date_created):
        result = list(self.connection.cursor().execute('SELECT * FROM Competencies WHERE name = ?', (name,)))
        if len(result) != 0:
            raise Exception('A competency with that name already exists')
        query = 'INSERT INTO Competencies (name, date_created) VALUES (?, ?)'
        values = (name, date_created)
        cursor = self.connection.cursor()
        cursor.execute(query, values)
        self.connection.commit()
        return Competency(cursor.lastrowid, *values)

    def create_assessment(self, competency_id, name, date_created):
        result = list(self.connection.cursor().execute('SELECT * FROM Competencies WHERE id = ?', (competency_id,)))
        if len(result) == 0:
            raise Exception(f'No competency with ID {competency_id} exists.')
        result = list(self.connection.cursor().execute('SELECT * FROM Assessments WHERE name = ? AND competency_id = ?', (name, competency_id)))
        if len(result) != 0:
            raise Exception(f'An assessment with the name {name} for competency {competency_id} already exists.')
        query = 'INSERT INTO Assessments (competency_id, name, date_created) VALUES (?, ?, ?)'
        values = (competency_id, name, date_created)
        cursor = self.connection.cursor()
        cursor.execute(query, values)
        self.connection.commit()
        return Assessment(cursor.lastrowid, *values)

    def create_assessment_result(self, user_id, assessment_id, score, date_taken, manager_id = 'NULL'):
        query = 'INSERT INTO Results (user_id, manager_id, assessment_id, score, date_taken) VALUES (?, ?, ?, ?, ?)'
        values = (user_id, manager_id, assessment_id, score, date_taken)
        cursor = self.connection.cursor()
        cursor.execute(query, values)
        self.connection.commit()
        return Result(cursor.lastrowid, *values)

    def get_user(self, id):
        result = list(self.connection.cursor().execute('SELECT * from Users WHERE id = ?', (id,)))
        if len(result) < 1:
            raise Exception('Invalid User ID')
        else:
            row = result[0]
            return User(id, row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10])

    def get_users(self):
        result = list(self.connection.cursor().execute('SELECT * FROM Users WHERE active = True'))
        return [User(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]) for row in result]

    def get_competency(self, id):
        result = list(self.connection.cursor().execute('SELECT * from Competencies WHERE id = ?', (id,)))
        if len(result) < 1:
            raise Exception('Invalid Competency ID')
        else:
            row = result[0]
            return Competency(id, row[1], row[2])

    def get_competencies(self):
        result = list(self.connection.cursor().execute('SELECT * FROM Competencies'))
        return [Competency(row[0], row[1], row[2]) for row in result]

    def get_assessment(self, id):
        result = list(self.connection.cursor().execute('SELECT * from Assessments WHERE id = ?', (id,)))
        if len(result) < 1:
            raise Exception('Invalid Assessment ID')
        else:
            row = result[0]
            return Assessment(id, row[1], row[2], row[3])

    def get_assessments(self):
        result = list(self.connection.cursor().execute('SELECT * FROM Assessments'))
        return [Assessment(row[0], row[1], row[2], row[3]) for row in result]

    def get_assessment_results(self):
        result = list(self.connection.cursor().execute('SELECT * FROM Results'))
        return [Result(row[0], row[1], row[2], row[3], row[4], row[5]) for row in result]

    def get_assessment_result(self, id):
        result = list(self.connection.cursor().execute('SELECT * from Results WHERE id = ?', (id,)))
        if len(result) < 1:
            raise Exception('Invalid Result ID')
        else:
            row = result[0]
            return Result(id, row[1], row[2], row[3], row[4], row[5])

    def get_assessment_result_by_user(self, user_id):
        result = list(self.connection.cursor().execute('SELECT * FROM Results WHERE user_id = ?', (user_id,)))
        return [Result(row[0], row[1], row[2], row[3], row[4], row[5]) for row in result]

    def update_user(self, user):
        query = 'UPDATE Users SET first_name = ?, last_name = ?, phone = ?, email = ?, password = ?, salt = ?, active = ?, date_created = ?, hire_date = ?, user_type = ? WHERE id = ?'
        values = (user.first_name, user.last_name, user.phone, user.email, user.password, user.salt, user.active, user.date_created, user.hire_date, user.user_type, user.id)
        self.connection.cursor().execute(query, values)
        self.connection.commit()
        print('User successfully updated')

    def update_competency(self, competency):
        query = 'UPDATE Competencies SET name = ?, date_created = ? WHERE id = ?'
        values = (competency.name, competency.date_created, competency.id)
        self.connection.cursor().execute(query, values)
        self.connection.commit()
        print('Competency successfully updated')

    def update_assessment(self, assessment):
        query = 'UPDATE Assessments SET competency_id = ?, name = ?, date_created = ? WHERE id = ?'
        values = (assessment.competency_id, assessment.name, assessment.date_created, assessment.id)
        self.connection.cursor().execute(query, values)
        self.connection.commit()
        print('Assessment successfully updated')

    def update_assessment_result(self, result):
        query = 'UPDATE Results SET user_id = ?, manager_id = ?, assessment_id = ?, score = ?, date_taken = ? WHERE id = ?'
        values = (result.user_id, result.manager_id, result.assessment_id, result.score, result.date_taken, result.id)
        self.connection.cursor().execute(query, values)
        self.connection.commit()
        print('Result successfully updated')

    def delete_user(self, id):
        self.connection.cursor().execute('DELETE FROM Users WHERE id = ?', (id,))
        self.connection.commit()

    def delete_competency(self, id):
        self.connection.cursor().execute('DELETE FROM Competencies WHERE id = ?', (id,))
        self.connection.commit()
        
    def delete_assessment(self, id):
        self.connection.cursor().execute('DELETE FROM Assessments WHERE id = ?', (id,))
        self.connection.commit()

    def delete_assessment_result(self, id):
        self.connection.cursor().execute('DELETE FROM Results WHERE id = ?', (id,))
        self.connection.commit()

    def search_users(self, search):
        result = list(self.connection.cursor().execute('SELECT * FROM Users WHERE first_name LIKE ? OR last_name LIKE ?', (f'%{search}%', f'%{search}%')))
        if len(result) == 0:
            raise Exception('No users were found')
        return [User(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]) for row in result]
