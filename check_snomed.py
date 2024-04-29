import sqlite3

def get_snomed_ids():
    #get ids from Mapping database 
    database = 'data/mapping.sqlite3'
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT target FROM mapping
    ''')
    snomed_ids = cursor.fetchall()
    snomed_ids = [snomed_id[0] for snomed_id in snomed_ids]
    get_snomed_names(snomed_ids)

def get_snomed_names(snomed_ids):
    dict = {}
    for snomed_id in snomed_ids:
        database = 'data/DutchSNOMEDCT.sqlite3'
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT term
            FROM Description 
            WHERE conceptId = ?
        ''', (snomed_id,))
        snomed_name = cursor.fetchone()
        if snomed_name:
            dict[snomed_id] = snomed_name[0]
        else :
            dict[snomed_id] = 'No name found'

    print_to_text(dict)

def print_to_text(dict):
    #print to text file
    with open('data/snomed_names.txt', 'w') as f:
        for key in dict.keys():
            f.write("%s: %s\n" % (key, dict[key]))

def main():
    get_snomed_ids()

if __name__ == '__main__':
    main()

