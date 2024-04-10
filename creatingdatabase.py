import sqlite3
from sqlite3 import Error
import csv


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def insert_subjects(conn):
    with open('data/subject_data.csv', 'r') as file:
        content = csv.reader(file)
        next(content) 
        sql = ''' INSERT OR IGNORE INTO subjects(subjectId, subjectTitle, subjectURL, subjectICPC)
                  VALUES(?,?,?,?) '''
    
        cur = conn.cursor()
        cur.executemany(sql, content)
        conn.commit()
        return cur.lastrowid
    
def insert_situations(conn):
    with open('data/situation_data.csv', 'r') as file:
        content = csv.reader(file)
        next(content)
        sql = ''' INSERT OR IGNORE INTO situations(subjectId, situationId, situationTitle, situationURL, situationICPC)
                  VALUES(?,?,?,?,?) '''
    
        cur = conn.cursor()
        cur.executemany(sql, content)
        conn.commit()
        return cur.lastrowid
    
def insert_tasks(conn):
    with open('data/task_data.csv', 'r') as file:
        content = csv.reader(file)
        next(content)
        sql = ''' INSERT OR IGNORE INTO tasks(situationId, situationTitle, text)
                  VALUES(?,?,?) '''
        
        cur = conn.cursor()
        cur.executemany(sql, content)
        conn.commit()
        return cur.lastrowid

def main():
    database = r"/Users/myrtekuipers/Documents/AIforHealth/Thesis/Thesis/data/diabetestype2.sqlite3"

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
            icpcTerm TEXT,
            situationId INTEGER,
            subjectId INTEGER,
            FOREIGN KEY (snomedlinkId) REFERENCES SNOMEDLinks(snomedlinkId)
            FOREIGN KEY (situationId) REFERENCES Situations(situationId)
            FOREIGN KEY (subjectID) REFERENCES Subjects(subjectId)
            );
            """

    conn = create_connection(database)

    if conn is not None:
        create_table(conn, sql_create_subjects_table)
        create_table(conn, sql_create_situations_table)
        create_table(conn, sql_create_tasks_table)
        create_table(conn, sql_create_term_candidates_table)
        create_table(conn, sql_create_snomed_links_table)
        create_table(conn, sql_create_db_links_table)
        insert_subjects(conn)
        insert_situations(conn)
        insert_tasks(conn)


    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()
