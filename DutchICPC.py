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
                return result[0]  # Return the text corresponding to the code
            else:
                return None 
        except Error as e:
            print("Error while querying the database1:", e)
            return None 

    def search_situations(self, code):
        #sql1 = '''SELECT situationId FROM Situations WHERE situationICPC = ?'''
        sql1 = '''SELECT situationId FROM Situations WHERE situationICPC = ? OR situationICPC LIKE ?'''


        try:
            database1 = r"/Users/myrtekuipers/Documents/AIforHealth/Thesis/Thesis/data/test2.sqlite3"
            conn = sqlite3.connect(database1)
            cur = conn.cursor()
            cur.execute(sql1, (code, '%' + code + '%'))
            result = cur.fetchall()
            if result:
                return [row[0] for row in result]
            else:
                return None  # Code not found
        except Error as e:
            print("Error while querying the database:", e)
            return None  # Return None in case of error


if __name__ == "__main__":

    icpc = ICPCDutch()
    code = "F73"
    result = icpc.search[code]
