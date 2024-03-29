import sqlite3
import csv
from EL import EntityLinking
from DutchSnomed import *
from DutchICPC import *
from Mapping import *

def create_connection(db_file):
    try:
        return sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
        return None

def insert_data(conn, table, file_path, columns):
    with open(file_path, 'r') as file:
        content = csv.DictReader(file)
        cur = conn.cursor()
        cur.executemany(f"INSERT OR IGNORE INTO {table} VALUES ({','.join('?' * len(columns))})", (row[col] for row in content for col in columns))
        conn.commit()

def find_row_by_field(file_path, target_field, target_value):
    with open(file_path, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row[target_field] == target_value:
                return row
    return None

def insert_terms_links(conn):
    target_title = "Ik heb diabetes type 2"
    row = find_row_by_field('data/task_data.csv', 'situation_title', target_title)
    if not row:
        return None

    text = row['content_text']
    el = EntityLinking(text)

    cur = conn.cursor()
    cur.execute("SELECT taskId FROM tasks WHERE situationTitle = ?", (row['situation_title'],))
    task_id_row = cur.fetchone()
    if not task_id_row:
        return None

    task_id = task_id_row[0]
    for candidate in el.AllCandidates:
        term = candidate.variations[candidate.match_variation].text
        start_position = candidate.variations[candidate.match_variation].start_char
        end_position = candidate.variations[candidate.match_variation].end_char
        cur.execute("INSERT OR IGNORE INTO TermCandidates VALUES (?,?,?,?)", (task_id, term, start_position, end_position))
        term_row_id = cur.lastrowid
        conn.commit()

        for index, snomed_link in enumerate(candidate.SimilarEntities):
            cur.execute("INSERT OR IGNORE INTO SNOMEDLinks VALUES (?,?,?,?,?)", (term_row_id, snomed_link.ConceptId, snomed_link.DescriptionID, snomed_link.Term, candidate.similarities[index]))
            snomed_link_id = cur.lastrowid
            conn.commit()

            icpc = Mapping().SNOMED2ICPC(snomed_link.ConceptId)
            if icpc:
                for code in icpc:
                    icpc_term = ICPCDutch().search(code)
                    situation_id = ICPCDutch().search_situations(code)
                    for s_id in situation_id if situation_id else [None]:
                        cur.execute("INSERT OR IGNORE INTO DBLinks VALUES (?,?,?,?)", (snomed_link_id, code, icpc_term, s_id))
                        conn.commit()

def main():
    database = r"/Users/myrtekuipers/Documents/AIforHealth/Thesis/Thesis/data/test1.sqlite3"
    conn = create_connection(database)
    if not conn:
        return
    
    with conn:
        insert_data(conn, 'subjects', 'data/subject_data.csv', ['subjectId', 'subjectTitle', 'subjectURL', 'subjectICPC'])
        insert_data(conn, 'situations', 'data/situation_data.csv', ['subjectId', 'situationId', 'situationTitle', 'situationURL', 'situationICPC'])
        insert_data(conn, 'tasks', 'data/task_data.csv', ['situationId', 'situationTitle', 'text'])
        insert_terms_links(conn)

if __name__ == '__main__':
    main()
