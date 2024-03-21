import sqlite3
from sqlite3 import Error
import csv


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def insert_subjects(conn):
    with open('data/subject_data.csv', 'r') as file:
        content = csv.reader(file)
        next(content)  # Skip header row
        sql = ''' INSERT INTO subjects(subjectId, subjectTitle, subjectURL, subjectICPC)
                  VALUES(?,?,?,?) '''
    
        cur = conn.cursor()
        cur.executemany(sql, content)
        conn.commit()
        return cur.lastrowid
    
def insert_situations(conn):
    with open('data/situation_data.csv', 'r') as file:
        content = csv.reader(file)
        next(content)  # Skip header row
        sql = ''' INSERT INTO situations(subjectId, situationId, situationTitle, situationURL, situationICPC)
                  VALUES(?,?,?,?,?) '''
    
        cur = conn.cursor()
        cur.executemany(sql, content)
        conn.commit()
        return cur.lastrowid
    
def insert_tasks(conn):
    with open('data/task_data.csv', 'r') as file:
        content = csv.reader(file)
        next(content)
        sql = ''' INSERT INTO tasks(situationId, situationTitle, text)
                  VALUES(?,?,?) '''
        
        cur = conn.cursor()
        cur.executemany(sql, content)
        conn.commit()
        return cur.lastrowid

# def update_subject(conn, subject):
#     sql = ''' UPDATE subjects
#               SET subjectTitle = ? ,
#                   subjectURL = ?,
#                   subjectICPC = ?
#               WHERE subjectId = ?'''
#     cur = conn.cursor()
#     cur.execute(sql, subject)
#     conn.commit()

# def delete_subject(conn, id):
#     sql = 'DELETE FROM subjects WHERE subjectId=?'
#     cur = conn.cursor()
#     cur.execute(sql, (id,))
#     conn.commit()

# def delete_all_subjects(conn):
#     sql = 'DELETE FROM subjects'
#     cur = conn.cursor()
#     cur.execute(sql)
#     conn.commit()

def main():
    database = r"/Users/myrtekuipers/Documents/AIforHealth/Thesis/Thesis/data/links.sqlite3"

    conn = create_connection(database)
    with conn:
        insert_tasks(conn)

if __name__ == '__main__':
    main()