
class Result:
    def __init__(self, id, user_id, manager_id, assessment_id, score, date_taken):
        self.id = id
        self.user_id = user_id
        self.manager_id = manager_id
        self.assessment_id = assessment_id
        self.score = score
        self.date_taken = date_taken

    def csv_row(self):
        return (f'{self.user_id},{self.manager_id},{self.assessment_id},{self.score},{self.date_taken}')

    @classmethod
    def table_header(cls):
        return f'ID  User Assessment Score Date Taken\n' + (36*'_')

    def __repr__(self):
        return(f'{self.id:<4}{self.user_id:<5}{self.assessment_id:<11}{self.score:<6}{self.date_taken:<10}')