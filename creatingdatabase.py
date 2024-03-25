import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def main():
    database = r"/Users/myrtekuipers/Documents/AIforHealth/Thesis/Thesis/data/links5.sqlite3"

    sql_create_subjects_table = """ CREATE TABLE IF NOT EXISTS Subjects (
            subjectId INTEGER PRIMARY KEY,
            subjectTitle TEXT,
            subjectURL TEXT,
            subjectICPC TEXT
        );
        """

    sql_create_situations_table = """ CREATE TABLE IF NOT EXISTS Situations (
                subjectId INTEGER,
                situationId INTEGER PRIMARY KEY,
                situationTitle TEXT,
                situationURL TEXT,
                situationICPC TEXT,
                FOREIGN KEY (subjectId) REFERENCES Subjects(subjectId)
            );
            """

    sql_create_tasks_table = """ CREATE TABLE IF NOT EXISTS Tasks (
                taskId INTEGER PRIMARY KEY,
                situationId INTEGER,
                situationTitle TEXT,
                text TEXT,
                FOREIGN KEY (situationId) REFERENCES Situations(situationId)
            );
            """


    sql_create_term_candidates_table = """ CREATE TABLE IF NOT EXISTS TermCandidates (
            termId INTEGER PRIMARY KEY,
            taskId INTEGER,
            term TEXT,
            startPosition INTEGER,
            endPosition INTEGER,
            FOREIGN KEY (taskId) REFERENCES Tasks(taskId)
            );
            """

    sql_create_snomed_links_table = """ CREATE TABLE IF NOT EXISTS SNOMEDLinks (
            snomedlinkId INTEGER PRIMARY KEY,
            termId INTEGER,
            conceptId TEXT,
            descriptionId TEXT,
            similarity REAL,
            FOREIGN KEY (termId) REFERENCES TermCandidates(termId)
            );
            """
    #heb nu typeID, concept geskipt hierboven, maar moet er eigenlijk wel bij

    sql_create_db_links_table = """ CREATE TABLE IF NOT EXISTS DBLinks (
            linkId INTEGER PRIMARY KEY,
            snomedlinkId INTEGER,
            icpc TEXT,
            icpcTerm TEXT,
            situationId INTEGER,
            FOREIGN KEY (snomedlinkId) REFERENCES SNOMEDLinks(snomedlinkId)
            );
            """

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        create_table(conn, sql_create_subjects_table)

        create_table(conn, sql_create_situations_table)

        create_table(conn, sql_create_tasks_table)

        create_table(conn, sql_create_term_candidates_table)

        create_table(conn, sql_create_snomed_links_table)

        create_table(conn, sql_create_db_links_table)
    else:
        print("Error! cannot create the database connection.")


if __name__ == '__main__':
    main()
