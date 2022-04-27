import bcrypt

class User:
    def __init__(self, id, first_name, last_name, phone, email, password, salt, active, date_created, hire_date, user_type):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.password = password
        self.salt = salt
        self.active = active
        self.date_created = date_created
        self.hire_date = hire_date
        self.user_type = user_type 

    def set_password(self, password):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        self.password = hashed
        self.salt = salt

    def print_info(self):
        print(repr(self))

    def csv_row(self):
        return (f'{self.first_name},{self.last_name},{self.phone},{self.email},{self.password},{self.salt},{self.active},{self.hire_date},{self.user_type}')

    @classmethod
    def table_header(cls):
        return f'ID   First Name  Last Name   Phone          Email               Status    Hire Date     User Type\n' + (97*'_')

    def __repr__(self):
        active_status = 'inactive' if self.active == 0 else 'active'
        return (f'{self.id:<5}{self.first_name:<12}{self.last_name:<12}{self.phone:<15}{self.email:<20}{active_status:<10}{self.hire_date:<14}{self.user_type:<10}')
