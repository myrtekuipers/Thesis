import sqlite3
from sqlite3 import Error

class ICPCDutch:

    def __init__(self):
        pass

    def __getitem__(self, code):
        return self.search(code)
    
    def search(self, code):
        sql = '''SELECT finalcodes.tekst FROM finalcodes WHERE finalcodes.code = ?'''
        try:
            database = r"/Users/myrtekuipers/Documents/AIforHealth/Thesis/Thesis/data/icpc.sqlite3"
            conn = sqlite3.connect(database)
            cur = conn.cursor()
            cur.execute(sql, (code,))
            result = cur.fetchone()
            if result:
                return result[0]  
            else:
                return None 
        except Error as e:
            print("Error while querying the database1:", e)
            return None 

    def search_situations(self, code, database):
        sql1 = '''SELECT situationId FROM Situations WHERE situationICPC = ? OR situationICPC LIKE ?'''
        results = []

        try:
            conn = sqlite3.connect(database)
            cur = conn.cursor()
            
            cur.execute(sql1, (code, '%' + code + '%'))
            result = cur.fetchall()

            results.extend([(row[0], 0) for row in result])

            if '.' in code:
                general_code = code.split('.')[0]
                cur.execute(sql1, (general_code, '%' + general_code + '%'))
                result = cur.fetchall()

                results.extend([(row[0], -1) for row in result])

            if results:
                return results
            else:
                return None  
        except Error as e:
            print("Error while querying the database:", e)
            return None 


if __name__ == "__main__":

    icpc = ICPCDutch()
    code = "F73"
    result = icpc.search[code]
