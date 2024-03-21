import sqlite3
import csv
from EL import EntityLinking
import DutchSnomed

def create_connection(db_file):
    try:
        return sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
        return None

def insert_data_from_csv(conn, table_name, csv_file_path, columns):
    with open(csv_file_path, 'r') as file:
        content = csv.reader(file)
        next(content)  # Skip header row
        sql = f"INSERT OR IGNORE INTO {table_name}({', '.join(columns)}) VALUES({', '.join(['?']*len(columns))})"
        cur = conn.cursor()
        cur.executemany(sql, content)
        conn.commit()
        return cur.lastrowid

def insert_termcandidates(conn):
    with open('data/task_data.csv', 'r') as file:
        content = csv.reader(file)
        next(content)
        first_row = next(content) 
        text = first_row[2]
        el = EntityLinking(text)
        cur = conn.cursor()
        situation_title = first_row[1]
        cur.execute("SELECT taskId FROM tasks WHERE situationTitle = ?", (situation_title,))
        task_id_row = cur.fetchone()
        last_row_id = 0
        if task_id_row:
            task_id = task_id_row[0]
            for candidate in el.AllCandidates:
                term = candidate.variations[candidate.match_variation].text
                startPosition = candidate.variations[candidate.match_variation].start_char
                endPosition = candidate.variations[candidate.match_variation].end_char
                content = (task_id, term, startPosition, endPosition)
                sql = ''' INSERT OR IGNORE INTO TermCandidates(taskId, term, startPosition, endPosition) VALUES(?,?,?,?) '''
                cur.execute(sql, content)
                last_row_id = cur.lastrowid 
        return last_row_id

def insert_snomed_links(conn):
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT termId, term FROM termcandidates")
        term_rows = cur.fetchall()
        for term_row in term_rows:
            term_id, term = term_row
            snomed = DutchSnomed.SNOMED(term)
            for snomed_link in snomed:
                content = (term_id, snomed_link.conceptId, snomed_link.descriptionId, snomed_link.typeId, snomed_link.concept, snomed_link.similarity)
                sql = ''' INSERT OR IGNORE INTO SNOMEDLinks(termId, conceptId, descriptionId, typeId, concept, similarity) VALUES(?,?,?,?,?,?) '''
                cur.execute(sql, content)
                conn.commit()

def main():
    database = r"/Users/myrtekuipers/Documents/AIforHealth/Thesis/Thesis/data/links2.sqlite3"
    conn = create_connection(database)
    with conn:
        # Specify the table name, CSV file path, and columns for each insert operation
        insert_data_from_csv(conn, 'subjects', 'data/subject_data.csv', ['subjectId', 'subjectTitle', 'subjectURL', 'subjectICPC'])
        insert_data_from_csv(conn, 'situations', 'data/situation_data.csv', ['subjectId', 'situationId', 'situationTitle', 'situationURL', 'situationICPC'])
        insert_data_from_csv(conn, 'tasks', 'data/task_data.csv', ['situationId', 'situationTitle', 'text'])
        insert_termcandidates(conn)
        insert_snomed_links(conn)

if __name__ == '__main__':
    main()
