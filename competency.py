
class Competency:
    def __init__(self, id, name, date_created):
        self.id = id
        self.name = name
        self.date_created = date_created

    def csv_row(self):
        return (f'{self.name},{self.date_created}')

    @classmethod
    def table_header(cls):
        return f'ID  Competency Name             Date Taken\n' + (42*'_')

    def __repr__(self):
        return(f'{self.id:<4}{self.name:<28}{self.date_created:<10}')
