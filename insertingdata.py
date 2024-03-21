import sqlite3
from sqlite3 import Error
import csv
from EL import EntityLinking
import DutchSnomed


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
        sql = ''' INSERT OR IGNORE INTO subjects(subjectId, subjectTitle, subjectURL, subjectICPC)
                  VALUES(?,?,?,?) '''
    
        cur = conn.cursor()
        cur.executemany(sql, content)
        conn.commit()
        return cur.lastrowid
    
def insert_situations(conn):
    with open('data/situation_data.csv', 'r') as file:
        content = csv.reader(file)
        next(content)  # Skip header row
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
    
# def insert_termcandidates(conn):
#     with open('data/task_data.csv', 'r') as file:
#         content = csv.reader(file)
#         next(content)
#         first_row = next(content) 
            
#         text = first_row[2]

#         el = EntityLinking(text)

#         last_row_id = 0
#         for candidate in el.AllCandidates:
#             term = candidate.variations[candidate.match_variation].text
#             startPosition = candidate.variations[candidate.match_variation].start_char
#             endPosition = candidate.variations[candidate.match_variation].end_char
#             content1 = (taskId, term, startPosition, endPosition)

#             sql = ''' INSERT OR IGNORE INTO TermCandidates(taskId, term, startPosition, endPosition)
#                     VALUES(?,?,?,?) '''
        
#             cur = conn.cursor()
#             cur.execute(sql, content1)
#             conn.commit()
#             last_row_id = cur.lastrowid 
        
#         return last_row_id
    
def insert_termcandidates(conn):
    with open('data/task_data.csv', 'r') as file:
        content = csv.reader(file)
        next(content)
        first_row = next(content) 
            
        text = first_row[2]

        el = EntityLinking(text)

        last_row_id = 0
        cur = conn.cursor()

        situation_title = first_row[1]  # Assuming situationTitle is in the second column
        cur.execute("SELECT taskId FROM tasks WHERE situationTitle = ?", (situation_title,))
        task_id_row = cur.fetchone()
        if task_id_row:
            task_id = task_id_row[0]

            for candidate in el.AllCandidates:
                term = candidate.variations[candidate.match_variation].text
                startPosition = candidate.variations[candidate.match_variation].start_char
                endPosition = candidate.variations[candidate.match_variation].end_char
                content1 = (task_id, term, startPosition, endPosition)

                sql = ''' INSERT OR IGNORE INTO TermCandidates(taskId, term, startPosition, endPosition)
                        VALUES(?,?,?,?) '''
            
                cur.execute(sql, content1)
                last_row_id = cur.lastrowid 
        
        return last_row_id


# def update_subject(conn, subject):
#     sql = ''' UPDATE subjects
#               SET subjectTitle = ? ,
#                   subjectURL = ?,
#                   subjectICPC = ?
#               WHERE subjectId = ?'''
#     cur = conn.cursor()
#     cur.execute(sql, subject)
#     conn.commit()

# def delete_rows(conn):
#     sql = 'DELETE FROM tasks WHERE rowId >= 1575'
#     cur = conn.cursor()
#     cur.execute(sql)
#     conn.commit()

# def delete_all_rows(conn):
#     sql = 'DELETE FROM termcandidates'
#     cur = conn.cursor()
#     cur.execute(sql)
#     conn.commit()

def main():
    database = r"/Users/myrtekuipers/Documents/AIforHealth/Thesis/Thesis/data/links1.sqlite3"

    conn = create_connection(database)
    with conn:
        # insert_subjects(conn)
        # insert_situations(conn)
        # insert_tasks(conn)
        #insert_termcandidates(conn)
        insert_snomed_links(conn)

if __name__ == '__main__':
    main()