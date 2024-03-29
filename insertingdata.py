import sqlite3
from sqlite3 import Error
import csv
from EL import EntityLinking
from DutchSnomed import *
from DutchICPC import *
from Mapping import *


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
    
def find_row_by_situation_title(file_path, target_title):
    with open(file_path, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['situation_title'] == target_title:
                return row
    return None
    
# def insert_terms_links(conn):
#     # with open('data/task_data.csv', 'r') as file:
#     #     content = csv.reader(file)
#     #     next(content)
#         # next(content)
#         # second_row = next(content) 

#         target_title = "Ik heb diabetes type 2"
#         row = find_row_by_situation_title('data/task_data.csv', target_title)

#         text = row['content_text'] 
#         el = EntityLinking(text)

#         last_row_id = 0
#         cur = conn.cursor()

#         situation_title = row['situation_title']
#         cur.execute("SELECT taskId FROM tasks WHERE situationTitle = ?", (situation_title,))
#         task_id_row = cur.fetchone()
#         if task_id_row:
#             task_id = task_id_row[0]

#             for candidate in el.AllCandidates:
#                 term = candidate.variations[candidate.match_variation].text
#                 startPosition = candidate.variations[candidate.match_variation].start_char
#                 endPosition = candidate.variations[candidate.match_variation].end_char
#                 content1 = (task_id, term, startPosition, endPosition)

#                 sql = ''' INSERT OR IGNORE INTO TermCandidates(taskId, term, startPosition, endPosition)
#                         VALUES(?,?,?,?) '''
            
#                 cur.execute(sql, content1)
#                 term_row_id = cur.lastrowid
#                 conn.commit()

#                 for index, snomed_link in enumerate(candidate.SimilarEntities):
#                     content2 = (term_row_id, snomed_link.ConceptId, snomed_link.DescriptionID, snomed_link.Term, candidate.similarities[index])
#                     sql = ''' INSERT OR IGNORE INTO SNOMEDLinks(termId, conceptId, descriptionId, concept, similarity)
#                             VALUES(?,?,?,?,?) '''
#                     cur.execute(sql, content2)
#                     last_row_id = cur.lastrowid 
#                     conn.commit()

#                     icpc = Mapping().SNOMED2ICPC(snomed_link.ConceptId)
#                     if icpc:
#                         for code in icpc:
#                             icpcTerm = ICPCDutch().search(code)
#                             situationId = ICPCDutch().search_situations(code)
#                             situationIds = situationId if situationId else None
#                             for situationId in situationIds if situationIds else [None]:
#                                 content3 = (last_row_id, code, icpcTerm, situationId)
#                                 sql = ''' INSERT OR IGNORE INTO DBLinks(snomedlinkId, icpc, icpcTerm, situationId)
#                                         VALUES(?,?,?,?) '''
#                                 cur.execute(sql, content3)
#                                 conn.commit()

#         return last_row_id

def process_tasks(conn, target_titles):
    last_row_ids = []
    cur = conn.cursor()

    for target_title in target_titles:
        row = find_row_by_situation_title('data/task_data.csv', target_title)

        text = row['content_text'] 
        el = EntityLinking(text)

        situation_title = row['situation_title']
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
                term_row_id = cur.lastrowid
                conn.commit()

                for index, snomed_link in enumerate(candidate.SimilarEntities):
                    content2 = (term_row_id, snomed_link.ConceptId, snomed_link.DescriptionID, snomed_link.Term, candidate.similarities[index])
                    sql = ''' INSERT OR IGNORE INTO SNOMEDLinks(termId, conceptId, descriptionId, concept, similarity)
                            VALUES(?,?,?,?,?) '''
                    cur.execute(sql, content2)
                    last_row_id = cur.lastrowid 
                    conn.commit()

                    icpc = Mapping().SNOMED2ICPC(snomed_link.ConceptId)
                    if icpc:
                        for code in icpc:
                            icpcTerm = ICPCDutch().search(code)
                            situationId = ICPCDutch().search_situations(code)
                            situationIds = situationId if situationId else None
                            for situationId in situationIds if situationIds else [None]:
                                content3 = (last_row_id, code, icpcTerm, situationId)
                                sql = ''' INSERT OR IGNORE INTO DBLinks(snomedlinkId, icpc, icpcTerm, situationId)
                                        VALUES(?,?,?,?) '''
                                cur.execute(sql, content3)
                                conn.commit()

            last_row_ids.append(last_row_id)

    return last_row_ids


# def delete_rows(conn):
#     sql = 'DELETE FROM termcandidates WHERE rowId >= 153'
#     cur = conn.cursor()
#     cur.execute(sql)
#     conn.commit()
    
def delete_all_tables(conn):
    cur = conn.cursor()
    cur.execute("DELETE FROM termcandidates")
    cur.execute("DELETE FROM snomedlinks")
    cur.execute("DELETE FROM dblinks")
    conn.commit()

def main():
    database = r"/Users/myrtekuipers/Documents/AIforHealth/Thesis/Thesis/data/test2.sqlite3"

    conn = create_connection(database)

    target_titles = ["Ik heb diabetes type 2", "Ik heb mogelijk darmkanker"]
    with conn:
        insert_subjects(conn)
        insert_situations(conn)
        insert_tasks(conn)
        process_tasks(conn, target_titles)
        #delete_all_tables(conn)
        

if __name__ == '__main__':
    main()