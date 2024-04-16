import sqlite3
from sqlite3 import Error 

database = 'databases/acne.sqlite3'

try: 
    conn = sqlite3.connect(database)
except Error as e:
    print(e)

cur = conn.cursor()

def get_subject_info(source_subject):
    cur.execute('''
        SELECT subjectId, subjectTitle, subjectICPC
        FROM subjects 
        WHERE subjectTitle = ?
    ''', (source_subject,))

    subject_info_task = cur.fetchone()  

    return subject_info_task

def get_related_subjects():
    cur.execute('''
        SELECT d.subjectId, s.subjectTitle, s.subjectICPC
        FROM dblinks d
        JOIN subjects s ON d.subjectId = s.subjectId

    ''')

    related_subject_data = cur.fetchall()

    return related_subject_data

def get_related_subjects_freq(related_subject_data):
    cur.execute('''
        SELECT sl.snomedlinkId, GROUP_CONCAT(DISTINCT d.subjectId) AS subject_ids
        FROM dblinks d
        JOIN snomedlinks sl ON d.snomedlinkId = sl.snomedlinkId
        GROUP BY sl.snomedlinkId
    ''')

    results = cur.fetchall()

    subject_occurrences = {}

    for row in results:
        value = row[1]
        if value is not None:
            subject_ids = value.split(',') 
            for subject_id1 in subject_ids:
                if subject_id1 in [str(row[0]) for row in related_subject_data]: 
                    if subject_id1 not in subject_occurrences:
                        subject_occurrences[subject_id1] = 1
                    else:
                        subject_occurrences[subject_id1] += 1

    sorted_occurrences = sorted(subject_occurrences.items(), key=lambda x: x[1], reverse=True)

    return sorted_occurrences


def print_results(subject_info_task, sorted_occurrences):
    source_id, subjectTitle, subjectICPC = subject_info_task
    print(f"Subject {source_id}: {subjectTitle} ({subjectICPC})")
    print("Related subjects:")

    for subject_id, occurrences in sorted_occurrences:
        cur.execute('''
            SELECT subjectTitle, subjectICPC
            FROM subjects
            WHERE subjectId = ?
        ''', (subject_id,))

        subject_title, subject_icpc = cur.fetchone()
        print(f"  - {subject_id} {subject_title} ({subject_icpc}) ({occurrences} occurrences)")

def save_results(subject_info_task, sorted_occurrences):
    source_id, subjectTitle, subjectICPC = subject_info_task
    with open('acne_related.txt', 'w') as f:
        f.write(f"Subject {source_id}: {subjectTitle} ({subjectICPC})\n")
        f.write("Related subjects:\n")

        for subject_id, occurrences in sorted_occurrences:
            cur.execute('''
                SELECT subjectTitle, subjectICPC
                FROM subjects
                WHERE subjectId = ?
            ''', (subject_id,))

            subject_title, subject_icpc = cur.fetchone()
            f.write(f"  - {subject_id} {subject_title} ({subject_icpc}) ({occurrences} occurrences)\n")

def main():
    source_subject = ["Acne"]
                    #   "Buikpijn", "Hoesten", "Keelpijn", "Pijn op de borst", "Uitstrijkje baarmoederhals"]

    subject_info_task = get_subject_info(source_subject)
    related_subject_data = get_related_subjects()
    subject_occurrences = get_related_subjects_freq(related_subject_data)
    #print_results(subject_info_task, subject_occurrences)
    save_results(subject_info_task, subject_occurrences)

if __name__ == '__main__':
    main()