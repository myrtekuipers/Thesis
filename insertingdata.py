import sqlite3
from sqlite3 import Error
import csv
from EL import EntityLinking
from DutchSnomed import *
from DutchICPC import *
from mapping2 import *


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
    
def insert_terms_links(conn):
    with open('data/task_data.csv', 'r') as file:
        content = csv.reader(file)
        next(content)
        first_row = next(content) 
            
        text = first_row[2] #get the text from the situations page

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

                for index, snomed_link in enumerate(candidate.SimilarEntities):
                    content2 = (last_row_id, snomed_link.ConceptId, snomed_link.DescriptionID, snomed_link.Term, snomed_link.TypeCode, candidate.similarities[index])
                    sql = ''' INSERT OR IGNORE INTO SNOMEDLinks(termId, conceptId, descriptionId, concept, type, similarity)
                            VALUES(?,?,?,?,?,?) '''
                    cur.execute(sql, content2)
                    conn.commit()

                    #check if that snomed link has a corresponding ICPC code
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

        return last_row_id

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
    database = r"/Users/myrtekuipers/Documents/AIforHealth/Thesis/Thesis/data/finaldb2.sqlite3"

    conn = create_connection(database)
    with conn:
        # insert_subjects(conn)
        # insert_situations(conn)
        # insert_tasks(conn)
        # insert_terms_links(conn)
        #delete_all_tables(conn)
        pass
        

if __name__ == '__main__':
    main()