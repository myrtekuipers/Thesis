import sqlite3
from sqlite3 import Error

class ICPCDutch():

    def __init__(self):
        pass

    def __getitem__(self, code):
        return ICPCConcept(code)
    
    def connectToSql(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)

        return conn
    
    def search(self, code):
        sql = ''' Select finalcodes.code FROM finalcodes WHERE finalcodes.code = ? '''
        cur = conn.cursor()
        cur.execute(sql, (code,))

class ICPCConcept():
    pass


    pass

if __name__ == "__main__":
    database = r"/Users/myrtekuipers/Documents/AIforHealth/Thesis/Thesis/data/icpc.sqlite3"


