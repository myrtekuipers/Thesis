import json
import pandas as pd
import sqlite3

with open('data/ICPC-SNOMED-20230711.json') as f:
    data = json.load(f)

mapping = pd.DataFrame(data['group'][0]['element'])

mapping['target'] = mapping['target'].apply(lambda x: x[0]['code'])

mapping = mapping[['target', 'code']]

conn = sqlite3.connect('data/mapping.sqlite3')

mapping.to_sql('mapping', conn, if_exists='replace', index=False)

conn.close()


