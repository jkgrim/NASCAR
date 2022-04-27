
class Assessment:
    def __init__(self, id, competency_id, name, date_created):
        self.id = id
        self.competency_id = competency_id
        self.name = name
        self.date_created = date_created

    def csv_row(self):
        return (f'{self.competency_id},{self.name},{self.date_created}')

    @classmethod
    def table_header(cls):
        return f'ID  Assessment Name                                              Date Taken\n' + (75*'_')

    def __repr__(self):
        return(f'{self.id:<4}{self.competency_id:<11}{self.name:<50}{self.date_created:<10}')