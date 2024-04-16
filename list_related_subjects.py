import sqlite3

database = 'databases/hoesten.sqlite3'

def connect_to_database(db_file):
    conn = sqlite3.connect(db_file)
    return conn.cursor()

def get_subject_info(cursor, source_subject):
    cursor.execute('''
        SELECT subjectId, subjectTitle, subjectICPC
        FROM subjects 
        WHERE subjectTitle = ?
    ''', (source_subject,))
    return cursor.fetchone()

def get_related_subjects(cursor):
    cursor.execute('''
        SELECT d.subjectId, s.subjectTitle, s.subjectICPC
        FROM dblinks d
        JOIN subjects s ON d.subjectId = s.subjectId
    ''')
    return cursor.fetchall()

def get_related_subjects_freq(cursor):
    cursor.execute('''
        SELECT sl.snomedlinkId, COUNT(DISTINCT d.subjectId) AS occurrences
        FROM dblinks d
        JOIN snomedlinks sl ON d.snomedlinkId = sl.snomedlinkId
        GROUP BY sl.snomedlinkId
        ORDER BY occurrences DESC
    ''')
    return cursor.fetchall()

def print_results(subject_info_task, related_subject_occurrences):
    source_id, subjectTitle, subjectICPC = subject_info_task
    print(f"Subject {source_id}: {subjectTitle} ({subjectICPC})")
    print("Related subjects:")

    for subject_id, occurrences in related_subject_occurrences:
        print(f"  - {subject_id} ({occurrences} occurrences)")

def main():
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    source_subject = "Hoesten"
    subject_info_task = get_subject_info(cursor, source_subject)
    related_subject_occurrences = get_related_subjects_freq(cursor)
    print_results(subject_info_task, related_subject_occurrences)

if __name__ == '__main__':
    main()
