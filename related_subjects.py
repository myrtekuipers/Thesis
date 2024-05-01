import sqlite3
from sqlite3 import Error 

database = 'databases/combined.sqlite3'

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

def get_task_ids(source_id):
    cur.execute('''
        SELECT t.taskId
        FROM tasks t
        JOIN situations s ON t.situationId = s.situationId
        JOIN subjects sub ON s.subjectId = sub.subjectId 
        WHERE sub.subjectId = ?
    ''', (source_id,))

    task_ids = cur.fetchall()

    return task_ids

def get_related_subjects_freq(task_ids, source_id):
    subject_occurrences = []

    for task_id in task_ids:
        task_id = task_id[0]

        cur.execute('''
        SELECT d.subjectId, s.subjectTitle, s.subjectICPC,
        COUNT(DISTINCT sl.snomedlinkId) AS occurrences
        FROM dblinks d
        JOIN subjects s ON d.subjectId = s.subjectId
        JOIN snomedlinks sl ON d.snomedlinkId = sl.snomedlinkId
        JOIN termcandidates tc ON sl.termId = tc.termId
        WHERE tc.taskId = ?
        GROUP BY d.subjectId;   
        ''' , (task_id,))

        results = cur.fetchall()

        if source_id in [row[0] for row in results]:
            results = [row for row in results if row[0] != source_id]

        subject_occurrences.extend(results)

        aggregated_data = {}

        for subject_id, title, icpc, frequency in subject_occurrences:
            if subject_id in aggregated_data:
                aggregated_data[subject_id]['frequency'] += frequency
            else:
                aggregated_data[subject_id] = {'title': title, 'icpc': icpc, 'frequency': frequency}

        aggregated_list = [(subject_id, data['title'], data['icpc'], data['frequency']) for subject_id, data in aggregated_data.items()]


    return aggregated_list

def print_results(subject_info_task, sorted_occurrences):
    source_id, subjectTitle, subjectICPC = subject_info_task
    print(f"Subject {source_id}: {subjectTitle} ({subjectICPC})")
    print("Related subjects:")

    for _, subject_title, subject_icpc, occurrences in sorted_occurrences:
        print(f"  - {subject_title} ({subject_icpc}) ({occurrences})")

def save_results(subject_info_task, sorted_occurrences):
    _, subjectTitle, subjectICPC = subject_info_task
    with open('links/all_related.txt', 'a') as f:
        f.write(f"\nSubject: {subjectTitle} ({subjectICPC})\n")
        f.write("Related subjects:\n")

        for _, subject_title, subject_icpc, occurrences in sorted_occurrences:
            f.write(f"{subject_title} ({subject_icpc}) ({occurrences})\n")
        f.write("\n")

def main():
    source_subjects = ["Acne", "Buikpijn", "Hoesten", "Keelpijn", "Gezond leven", "Diabetes type 2", "Problemen thuis", "Medicijnen bij ouderen", "Pijn op de borst", "Uitstrijkje baarmoederhals"]

    for source_subject in source_subjects:
        subject_info_task = get_source_subject_info(source_subject)
        source_id = subject_info_task[0]
        task_ids = get_task_ids(source_id)
        subject_occurrences = get_related_subjects_freq(task_ids, source_id)
        #print_results(subject_info_task, subject_occurrences)
        save_results(subject_info_task, subject_occurrences)
                      
if __name__ == '__main__':
    main()