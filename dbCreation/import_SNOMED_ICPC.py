import json
import pandas as pd
import sqlite3

with open('data/ICPC-SNOMED-20230711.json') as f:
    data = json.load(f)

mapping = pd.DataFrame(data['group'][0]['element'])

mapping['target'] = mapping['target'].apply(lambda x: x[0]['code'])

# def insert_commas(x):
#     str_x = str(x)
#     parts = []
#     while str_x:
#         parts.append(str_x[-3:])
#         str_x = str_x[:-3]
#     return ','.join(parts[::-1])

# mapping['target'] = mapping['target'].apply(insert_commas)

mapping = mapping[['target', 'code']]

conn = sqlite3.connect('data/mapping1.sqlite3')

mapping.to_sql('mapping', conn, if_exists='replace', index=False)

conn.close()


