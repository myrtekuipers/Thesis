import sqlite3

database= r"mapping.db"
conn = sqlite3.connect(database)
cursor = conn.cursor()

class Mapping:
    
    def __init__(self):
        pass

    def SNOMED2ICPC(self, snomed_id):
        query = "SELECT code FROM mapping WHERE target=?"
        cursor.execute(query, (snomed_id,))
        r = cursor.fetchall()
        
        if not r:
            return []
        
        icpc_codes = []
        for t in r: 
            icpc_codes.append(t[0]) 
        return icpc_codes

if __name__ == "__main__":
    map = Mapping(database)
    ls = map.SNOMED2ICPC(snomed_id="25656009")
    print(ls)
