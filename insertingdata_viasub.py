import sqlite3
from sqlite3 import Error
from EL import EntityLinking
from DutchSnomed import *
from DutchICPC import *
from Mapping import *

database = 'databases/combined.sqlite3'

try: 
    conn = sqlite3.connect(database)
except Error as e:
    print(e)

cur = conn.cursor()

def process_tasks(source_subjects):
    last_row_ids = []

    for source_title in source_subjects:
        cur.execute("SELECT subjectId FROM subjects WHERE subjectTitle = ?", (source_title,))
        source_subject_id = cur.fetchone()[0]

        cur.execute("""
            SELECT t.*
            FROM tasks t
            JOIN situations s ON t.situationId = s.situationId
            WHERE s.subjectId = ?
        """, (source_subject_id,))
        
        results = cur.fetchall()

        for row in results:
            text = row[3]
            el = EntityLinking(text)
            task_id = row[0]    

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
                            results = ICPCDutch().search_situations(code, database)
                            if results is not None:
                                for situationId, level in results:
                                    if situationId:
                                        subjectId = cur.execute("SELECT subjectId FROM situations WHERE situationId = ?", (situationId,)).fetchone()[0]
                                        level = level
                                    else:
                                        subjectId = None
                                        level = None
                                    
                                    #icpc term does now correspond to the code that was searched for, and if the more general code resulted in a situation, the icpc code (and term) in that row is still the specific code that was searched for, maybe change that?
                                    #or only change term? because the more general code is easily accessible from the specific code and then one level up. But the term could be different
                                    content3 = (last_row_id, code, level, icpcTerm, situationId, subjectId)
                                    sql = ''' INSERT OR IGNORE INTO DBLinks(snomedlinkId, icpc, level, icpcTerm, situationId, subjectId)
                                            VALUES(?,?,?,?,?,?) '''
                                    
                                    cur.execute(sql, content3)
                                    conn.commit()              

            last_row_ids.append(last_row_id)

    return last_row_ids

# def delete_rows(conn):
#     sql = 'DELETE FROM termcandidates WHERE rowId >= 153'
#     cur = conn.cursor()
#     cur.execute(sql)
#     conn.commit()
    
def delete_all_tables():
    cur.execute("DELETE FROM termcandidates")
    cur.execute("DELETE FROM snomedlinks")
    cur.execute("DELETE FROM dblinks")
    conn.commit()

def main():
    source_subjects = ["Acne", "Buikpijn", "Gezond leven","Hoesten", "Keelpijn", "Medicijnen bij ouderen", "Pijn op de borst", "Problemen thuis", "Uitstrijkje baarmoederhals"]

    process_tasks(source_subjects) 
    #delete_all_tables()


if __name__ == '__main__':
    main()