import sqlite3
import sys
import csv

from datetime import datetime
from getpass import getpass

from assessment import Assessment
from database import Database
from competency import Competency
from user import User
from result import Result

connection = sqlite3.connect('nascar.db')
cursor = connection.cursor()

class Nascar: # Newly Acquired Skill Competency Assessment Reporter
    def __init__(self, db_filename):
        self.db_filename = db_filename
        self.user = None
        self.running = True
        self.user_options = [
            '1. View competency and assessment data',
            '2. View user summary',
            '3. Edit user profile',
            '4. Logout'
        ]
        self.manager_options = [
            '1. View all users',
            '2. Search for users',
            '3. View competency report for all users',
            '4. View competency report for individual',
            '5. View list of assessments for a user',
            '6. Other options',
            '7. Logout'
        ]
        self.other_options = [
            'Add',
            '1. Add a user',
            '2. Add a new competency',
            '3. Add assessment to competency',
            '4. Add assessment result',
            'Edit',  
            '5. Edit user information',
            '6. Edit a competency',
            '7. Edit an assessment',
            '8. Edit an assessment result',
            'Import',
            '9. Import assessment results',
            'Export',
            '10. Export users to CSV',
            '11. Export results to CSV',
            '12. Export assessments to CSV',
            '13. Export competencies to CSV'
        ]
        
    def authenticate(self):
        print('Login')
        email = input('Email: ')
        password = getpass('Password: ')
        try: 
            self.user = Database(self.db_filename).authenticate(email, password) 
            print('Authentication successful')
        except:
            print('Authentication error.') 

    def print_users(self):
        users = Database(self.db_filename).get_users()
        print(User.table_header())
        for user in users:
            print(user)

    def print_competencies(self):
        competencies = Database(self.db_filename).get_competencies()
        print(Competency.table_header())
        for competency in competencies:
            print(competency)

    def print_assessments(self):
        assessments = Database(self.db_filename).get_assessments()
        print(Assessment.table_header())
        for assessment in assessments:
            print(assessment)
 
    def search_users(self):
        name_input = input('Enter a name: ')
        try:
            users = Database(self.db_filename).search_users(name_input)
            print(User.table_header())
            for user in users:
                print(user)
        except Exception as e:
            print(e)

    def get_assessment_result_by_user(self, user_id):
        results = Database(self.db_filename).get_assessment_result_by_user(user_id)
        if len(results) == 0:
            print('This user has no assessment results')
        else:
            print(Result.table_header())
            for result in results:
                print(result)

    def get_assessment_result_by_any_user(self):
        user_input = input('Enter a user ID: ')
        self.get_assessment_result_by_user(int(user_input))

    def later(self, date_one, date_two):
        return datetime.fromisoformat(date_one) > datetime.fromisoformat(date_two)

    def user_competency_summary(self, user_id):
        results = Database(self.db_filename).get_assessment_result_by_user(user_id)
        competencies = Database(self.db_filename).get_competencies()
        assessments = Database(self.db_filename).get_assessments()
        user = Database(self.db_filename).get_user(user_id)
        results_by_assessment = {}
        for assessment in assessments:
            results_by_assessment[assessment.id] = []
        for i, result in enumerate(results):
            results_by_assessment[result.assessment_id].append(i)
        assessments_by_competency = {}
        for competency in competencies: 
            assessments_by_competency[competency.id] = []
        for i, assessment in enumerate(assessments):
            assessments_by_competency[assessment.competency_id].append(i)
        with open(f'{user.first_name} {user.last_name}.csv', 'w') as file:
            file.write('competency,score\n')
            print('Competency                  Score\n' + (33*'_'))
            for competency in competencies:
                scores_sum = 0
                has_score = False
                for assessment_index in assessments_by_competency[competency.id]:
                    latest = None
                    score = 0
                    for result_index in results_by_assessment[assessments[assessment_index].id]:
                        has_score = True
                        if not latest or self.later(results[result_index].date_taken, latest):
                            latest = results[result_index].date_taken
                            score = results[result_index].score
                    scores_sum += score
                average = scores_sum/len(assessments_by_competency[competency.id])
                if has_score: 
                    file.write(f'{competency.name},{average:.2f}\n')
                    print(f'{competency.name:<28}{average:.2f}')

    def any_user_competency_summary(self):
        user_input = input('Enter a user ID: ')
        self.user_competency_summary(int(user_input))

    def competency_summary(self):
        user_input = input('Enter a competency ID: ')
        results = Database(self.db_filename).get_assessment_results()
        competency = Database(self.db_filename).get_competency(int(user_input))
        assessments = list(filter(lambda a: a.competency_id == competency.id, Database(self.db_filename).get_assessments()))
        users = Database(self.db_filename).get_users()
        results_by_assessment = {}
        for assessment in assessments:
            results_by_assessment[assessment.id] = {user.id:[] for user in users}
        for i, result in enumerate(results):
            if result.assessment_id in results_by_assessment:
                results_by_assessment[result.assessment_id][result.user_id].append(i)
        with open(f'{competency.name}.csv', 'w') as file:
            file.write('user,score\n')
            print('User                       Score\n' + (33*'_'))
            averages = []
            for user in users:
                scores_sum = 0
                for assessment in assessments:
                    latest = None
                    score = 0
                    for result_index in results_by_assessment[assessment.id][user.id]:
                        if not latest or self.later(results[result_index].date_taken, latest):
                            latest = results[result_index].date_taken
                            score = results[result_index].score
                    scores_sum += score
                average = scores_sum/len(assessments)
                averages.append(average)
            
                name = f'{user.first_name} {user.last_name}'
                print(f'{name:<28}{average:.2f}')
                file.write(f'{name},{average:.2f}\n')
            overall_average = sum(averages)/len(averages)
            print(f'Overall average for {competency.name}: {overall_average:.2f}')

    def add_user(self):
        print('\n### New User ###\nPlease fill out the form below to add a new User:\n')
        first_name = input('First Name: ')
        last_name = input('Last Name: ')
        phone = input('Phone: ')
        email = input('Email: ')
        password = input('Password: ')
        date_created = datetime.now().strftime('%Y-%m-%d')
        hire_date = input('Hire date: ')
        user_type = input('User type: ')
        try:
            new_user = Database(self.db_filename).create_user(first_name, last_name, phone, email, password, date_created, hire_date, user_type)
            print('\nUser successfully created\n')
        except Exception as e:
            print(e)

    def add_competency(self):
        print('\n### New Competency ###\nPlease fill out the form below to add a new Competency:\n')
        name = input('Competency name: ')
        date_created = datetime.now().strftime('%Y-%m-%d')
        try:
            new_competency = Database(self.db_filename).create_competency(name, date_created)
            print('\nCompetency successfully created\n')
        except Exception as e:
            print(e)

    def add_assessment(self):
        print('\n### New Assessment ###\nPlease fill out the form below to add a new Assessment to a competency:\n')
        competency_id = input('Competency ID: ')
        name = input('Assessment name: ')
        date_created = datetime.now().strftime('%Y-%m-%d')
        try:
            new_competency = Database(self.db_filename).create_assessment(competency_id, name, date_created)
            print('\nAssessment successfully created\n')
        except Exception as e:
            print(e)

    def add_assessment_result(self):
        print('\n### Add Assessment Result ###\nPlease fill out the form below to add a new Assessment Result:\n')
        user_id = input('User ID: ')
        assessment_id = input('Assessment ID: ')
        score = input('Score: ')
        date_taken = datetime.now().strftime('%Y-%m-%d')
        new_result = Database(self.db_filename).create_assessment_result(user_id, assessment_id, score, date_taken)
        print('\nAssessment Result successfully recorded\n')

    def edit_user(self, user_id):
        print('\n+++ User Detail +++\n')
        try:
            user = Database(self.db_filename).get_user(user_id)
            print(f'1. First Name: {user.first_name}')
            print(f'2. Last Name:  {user.last_name}')
            print(f'3. Phone:      {user.phone}')
            print(f'4. Email:      {user.email}')
            print(f'5. Password:   <hidden>')
            print(f'6. Active:     {user.active}')
            print(f'7. User Type:  {user.user_type}')
            print()
            print(f'8. Delete User')
            user_input = input("\nEnter the number of the field you would like to update.\nTo return to the main menu, press 'Enter'.\n>>> ")
            if user_input == '1':
                print(f'\nCurrent First Name: {user.first_name}')
                user.first_name = input('Updated First Name: ')
            elif user_input == '2':
                print(f'\nCurrent Last Name: {user.last_name}')
                user.last_name = input('Updated Last Name: ')
            elif user_input == '3':
                print(f'\nCurrent Phone Number: {user.phone}')
                user.phone = input('Updated Phone Number: ')
            elif user_input == '4':
                print(f'\nCurrent email: {user.email}')
                user.email = input('Updated Email: ')
            elif user_input == '5':
                user_input = getpass('Please enter current password: ')
                auth_user = Database(self.db_filename).authenticate(user.email, user_input)
                if auth_user and auth_user.id == user.id:
                    user_input = getpass('Updated Password: ')
                    user.set_password(user_input)
                else:
                    print('Incorrect password. Please try again.')
            elif user_input == '6':
                print(f'\nCurrent Active Status: {user.active}')
                user.active = input('Updated Active Status: ')
            elif user_input == '7':
                print(f'\nCurrent User Type: {user.user_type}')
                user.user_type = input('Updated User Type: ')
            Database(self.db_filename).update_user(user)
            if user_input == '8':
                Database(self.db_filename).delete_user(user.id)
                print(f'\nUser has been DELETED.')
                if user.id == self.user.id:
                    print('Currently logged in user has been deleted. Logging out.')
                    return('Deleted')
        except Exception as e:
            print(e)

    def edit_any_user(self):
        self.print_users()
        user_input = input('\nEnter a User ID to View a User: ')
        if user_input != '':
            return self.edit_user(int(user_input))

    def edit_competency(self):
        print('\n### Edit Competency ###\n')
        self.print_competencies()
        user_input = input('\nEnter a Competency ID to View a Competency: ')
        if user_input != '':
            print('\n+++ Competency Detail +++\n')
            try:
                competency = Database(self.db_filename).get_competency(int(user_input))
                print(f'1. Edit Name: {competency.name}')
                print()
                print(f'2. Delete Competency')
                user_input = input("\nEnter the number of the field you would like to update.\nTo return to the main menu, press 'Enter'.\n>>> ")
                if user_input == '1':
                    print(f'\nCurrent Competency Name: {competency.name}')
                    competency.name = input('Updated Competency Name: ')
                Database(self.db_filename).update_competency(competency)
                if user_input == '2':
                    Database(self.db_filename).delete_competency(competency.id)
                    print(f'\nCompetency has been DELETED.')
            except Exception as e:
                print(e)

    def edit_assessment(self):
        print('\n### Edit Assessment ###\n')
        self.print_assessments()
        user_input = input('\nEnter an Assessment ID to view Assement: ')
        if user_input != '':
            print('\n+++ Assessment Detail +++\n')
            try:
                assessment = Database(self.db_filename).get_assessment(int(user_input))
                print(f'1: Edit Name: {assessment.name}')
                print()
                print(f'2. Delete Competency')
                if user_input == '1':
                    print(f'\nCurrent Assessment Name: {assessment.name}')
                    value = input('Updated Assessment Name: ')
                Database(self.db_filename).update_assessment(assessment)
                if user_input == '2':
                    Database(self.db_filename).delete_assessment(assessment.id)
                    print(f'\nAssessment has been DELETED.')
            except Exception as e:
                print(e)

    def edit_assessment_result(self):
        print('\n### Edit Assessment Result ###\n')
        self.print_users()
        self.get_assessment_result_by_user()
        user_input = input('\nEnter a Result ID to view Result: ')
        if user_input != '':
            print('\n+++ Result Detail +++\n')
            try:
                result = Database(self.db_filename).get_assessment_result(int(user_input))
                print(f'1. Score: {result.score}')
                if user_input == '1':
                    print(f'\nCurrent Result Score: {result.score}')
                    value = input('Updated Result Score: ')
                Database(self.db_filename).update_assessment_result(result)
                if user_input == 'DELETE':
                    Database(self.db_filename).delete_assessment_result(result.id)
                    print(f'\nResult score has been DELETED.')
            except Exception as e:
                print(e)

    def users_to_csv(self):
        user_input = input('Enter name of file to export to: ')
        with open(user_input, 'w') as file:
            file.write('first_name,last_name,phone,email,password,salt,active,date_created,hire_date,user_type\n')
            users = Database(self.db_filename).get_users()
            for user in users:
                file.write(user.csv_row() + '\n')

    def results_to_csv(self):
        user_input = input('Enter name of file to export to: ')
        with open(user_input, 'w') as file:
            file.write('user_id,manager_id,assessment_id,score,date_taken\n')
            results = Database(self.db_filename).get_assessment_results()
            for result in results:
                file.write(result.csv_row() + '\n')

    def assessments_to_csv(self):
        user_input = input('Enter name of file to export to: ')
        with open(user_input, 'w') as file:
            file.write('competency_id,name,date_created\n')
            assessments = Database(self.db_filename).get_assessments()
            for assessment in assessments:
                file.write(assessment.csv_row() + '\n')

    def competencies_to_csv(self):
        user_input = input('Enter name of file to export to: ')
        with open(user_input, 'w') as file:
            file.write('name,date_created\n')
            competencies = Database(self.db_filename).get_competencies()
            for competency in competencies:
                file.write(competency.csv_row() + '\n')

    def results_from_csv(self):
        user_input = input('Enter a file name you would like to import: ')
        with open(user_input, 'r') as file:
            data = csv.DictReader(file)
            for row in data:
                Database(self.db_filename).create_assessment_result(row['user_id'],row['assessment_id'],row['score'],row['date_taken'],row['manager_id'])

    def run(self):
        while self.running:
            if not self.user:
                self.authenticate()
            else:
                if self.user.user_type == 'manager':
                    print('\n'.join(self.manager_options))
                    user_input = input('Select an option: ')
                    #Manager main loop
                    if user_input == '1': #view users
                        self.print_users()
                    elif user_input == '2': #search users
                        self.search_users()
                    elif user_input == '3': #view a report of all users and their competency levels for a given competency
                        self.competency_summary()
                    elif user_input == '4': #view a competency level report for an individual user
                        self.any_user_competency_summary()
                    elif user_input == '5': #list of assessments for given user
                        self.get_assessment_result_by_any_user() 
                    elif user_input == '6': #other options
                        print('\n'.join(self.other_options))
                        user_input = input('Select an option: ')
                        if user_input == '1': #add user
                            self.add_user()
                        elif user_input == '2': #add competency
                            self.add_competency()
                        elif user_input == '3': #add new assessment
                            self.add_assessment()
                        elif user_input == '4': #add new assessment results
                            self.add_assessment_result()
                        elif user_input == '5': #edit any user
                            deleted = self.edit_any_user()
                            if deleted:
                                self.user = None
                        elif user_input == '6': #edit competency
                            self.edit_competency()
                        elif user_input == '7': #edit assessment
                            self.edit_assessment()
                        elif user_input == '8': #edit assessment results
                            self.edit_assessment_result()
                        elif user_input == '9':
                            self.results_from_csv()
                        elif user_input == '10':
                            self.users_to_csv()
                        elif user_input == '11':
                            self.results_to_csv()
                        elif user_input == '12':
                            self.assessment_to_csv()
                        elif user_input == '13':
                            self.competency_to_csv()
                    elif user_input == '7': #logout
                        self.user = None
                    pass
                elif self.user.user_type == 'user':
                    print('\n'.join(self.user_options))
                    user_input = input('Select an option: ')
                    # User main loop
                    if user_input == '1': # view competency and assessment data
                        self.get_assessment_result_by_user(self.user.id)
                    elif user_input == '2':
                        self.user_competency_summary(self.user.id)
                    elif user_input == '3': # edit user profile
                        deleted = self.edit_user(self.user.id)
                        if deleted:
                            self.user = None
                    elif user_input == '4': # logout
                        self.user = None
                    pass
                else:
                    raise Exception('Invalid user type')
        pass

if __name__ == '__main__':
    app = Nascar(sys.argv[1])
    app.run()
    