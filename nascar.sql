CREATE TABLE Users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
first_name TEXT NOT NULL,
last_name TEXT NOT NULL,
phone TEXT,
email TEXT NOT NULL,
password TEXT NOT NULL,
salt TEXT NOT NULL,
active INTEGER DEFAULT 1 NOT NULL,
date_created TEXT NOT NULL,
hire_date TEXT NOT NULL,
user_type TEXT NOT NULL
)

CREATE TABLE Competencies (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
date_created TEXT NOT NULL
)

CREATE TABLE Assessments (
id INTEGER PRIMARY KEY AUTOINCREMENT,
competency_id INTEGER NOT NULL,
name TEXT NOT NULL,
date_created TEXT NOT NULL,
FOREIGN KEY (competency_id)
    REFERENCES Competencies (id)
)

CREATE TABLE Results (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER NOT NULL,
manager_id INTEGER NOT NULL,
assessment_id INTEGER NOT NULL,
score INTEGER NOT NULL,
date_taken TEXT NOT NULL,
FOREIGN KEY (user_id)
    REFERENCES Users (id),
FOREIGN KEY (manager_id)
    REFERENCES Users (id),
FOREIGN KEY (assessment_id)
    REFERENCES Assessments (id)
)