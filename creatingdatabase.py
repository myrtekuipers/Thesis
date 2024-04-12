import sqlite3
from sqlite3 import Error
import csv

database = 'databases/combinedcomplete.sqlite3'

try: 
    conn = sqlite3.connect(database)
except Error as e:
    print(e)

cur = conn.cursor()

def create_table(create_table_sql):
    try:
        cur.execute(create_table_sql)
    except Error as e:
        print(e)

def insert_subjects():
    with open('data/subject_data.csv', 'r') as file:
        content = csv.reader(file)
        next(content) 
        sql = ''' INSERT OR IGNORE INTO subjects(subjectId, subjectTitle, subjectURL, subjectICPC)
                  VALUES(?,?,?,?) '''
    
        cur.executemany(sql, content)
        conn.commit()
        return cur.lastrowid
    
def insert_situations():
    with open('data/situation_data.csv', 'r') as file:
        content = csv.reader(file)
        next(content)
        sql = ''' INSERT OR IGNORE INTO situations(subjectId, situationId, situationTitle, situationURL, situationICPC)
                  VALUES(?,?,?,?,?) '''
    
        cur.executemany(sql, content)
        conn.commit()
        return cur.lastrowid
    
def insert_tasks():
    with open('data/task_data.csv', 'r') as file:
        content = csv.reader(file)
        next(content)
        sql = ''' INSERT OR IGNORE INTO tasks(situationId, situationTitle, text)
                  VALUES(?,?,?) '''
        
        cur.executemany(sql, content)
        conn.commit()
        return cur.lastrowid

def main():
    sql_create_subjects_table = """ CREATE TABLE IF NOT EXISTS Subjects (
            subjectId INTEGER PRIMARY KEY,
            subjectTitle TEXT,
            subjectURL TEXT,
            subjectICPC TEXT
        );
        """

    sql_create_situations_table = """ CREATE TABLE IF NOT EXISTS Situations (
                situationId INTEGER PRIMARY KEY,
                subjectId INTEGER,
                situationTitle TEXT,
                situationURL TEXT,
                situationICPC TEXT,
                FOREIGN KEY (subjectId) REFERENCES Subjects(subjectId)
            );
            """

    sql_create_tasks_table = """ CREATE TABLE IF NOT EXISTS Tasks (
                taskId INTEGER PRIMARY KEY,
                situationId INTEGER,
                situationTitle TEXT,
                text TEXT
            );
            """


    sql_create_term_candidates_table = """ CREATE TABLE IF NOT EXISTS TermCandidates (
            termId INTEGER PRIMARY KEY,
            taskId INTEGER,
            term TEXT,
            startPosition INTEGER,
            endPosition INTEGER,
            FOREIGN KEY (taskId) REFERENCES Tasks(taskId)
            );
            """

    sql_create_snomed_links_table = """ CREATE TABLE IF NOT EXISTS SNOMEDLinks (
            snomedlinkId INTEGER PRIMARY KEY,
            termId INTEGER,
            conceptId INTEGER,
            descriptionId INTEGER,
            concept TEXT,
            similarity REAL,
            FOREIGN KEY (termId) REFERENCES TermCandidates(termId)
            );
            """

    sql_create_db_links_table = """ CREATE TABLE IF NOT EXISTS DBLinks (
            linkId INTEGER PRIMARY KEY,
            snomedlinkId INTEGER,
            icpc TEXT,
            level INTEGER,
            icpcTerm TEXT,
            situationId INTEGER,
            subjectId INTEGER,
            FOREIGN KEY (snomedlinkId) REFERENCES SNOMEDLinks(snomedlinkId)
            FOREIGN KEY (situationId) REFERENCES Situations(situationId)
            FOREIGN KEY (subjectID) REFERENCES Subjects(subjectId)
            );
            """

    create_table(sql_create_subjects_table)
    create_table(sql_create_situations_table)
    create_table(sql_create_tasks_table)
    create_table(sql_create_term_candidates_table)
    create_table(sql_create_snomed_links_table)
    create_table(sql_create_db_links_table)
    insert_subjects()
    insert_situations()
    insert_tasks()

if __name__ == '__main__':
    main()
