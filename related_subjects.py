import sqlite3
from sqlite3 import Error 

database = 'databases/keelpijn.sqlite3'

try: 
    conn = sqlite3.connect(database)
except Error as e:
    print(e)

cur = conn.cursor()

def get_source_subject_info(source_subject):
    cur.execute('''
        SELECT subjectId, subjectTitle, subjectICPC
        FROM subjects 
        WHERE subjectTitle = ?
    ''', (source_subject,))

    subject_info_task = cur.fetchone()  

    return subject_info_task

def get_related_subjects_freq(source_id):
    cur.execute('''
        SELECT d.subjectId, s.subjectTitle, s.subjectICPC,
        COUNT(DISTINCT sl.snomedlinkId) AS occurrences
        FROM dblinks d
        JOIN subjects s ON d.subjectId = s.subjectId
        JOIN snomedlinks sl ON d.snomedlinkId = sl.snomedlinkId
        GROUP BY d.subjectId;   
    ''')

    subject_occurrences = cur.fetchall()

    if source_id in [row[0] for row in subject_occurrences]:
        subject_occurrences = [row for row in subject_occurrences if row[0] != source_id]

    return subject_occurrences


def print_results(subject_info_task, sorted_occurrences):
    source_id, subjectTitle, subjectICPC = subject_info_task
    print(f"Subject {source_id}: {subjectTitle} ({subjectICPC})")
    print("Related subjects:")

    for _, subject_title, subject_icpc, occurrences in sorted_occurrences:
        print(f"  - {subject_title} ({subject_icpc}) ({occurrences})")

def save_results(subject_info_task, sorted_occurrences):
    _, subjectTitle, subjectICPC = subject_info_task
    with open('links/acne_related.txt', 'w') as f:
        f.write(f"Subject: {subjectTitle} ({subjectICPC})\n")
        f.write("Related subjects:\n")

        for _, subject_title, subject_icpc, occurrences in sorted_occurrences:
            f.write(f"{subject_title} ({subject_icpc}) ({occurrences})\n")

def main():
    source_subject = "Keelpijn"
                    #   "Buikpijn", "Hoesten", "Keelpijn", "Pijn op de borst", "Uitstrijkje baarmoederhals"]

    subject_info_task = get_source_subject_info(source_subject)
    source_id = subject_info_task[0]
    subject_occurrences = get_related_subjects_freq(source_id)
    print_results(subject_info_task, subject_occurrences)
    #save_results(subject_info_task, subject_occurrences)

if __name__ == '__main__':
    main()