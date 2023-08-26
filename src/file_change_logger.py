import sys
import sqlite3
import os
import time

# pip install cachetools
from cachetools import TTLCache

recent_logged_paths =  TTLCache(maxsize=200, ttl=600)

def was_logged_recently(path):
    if recent_logged_paths.get(path, None):
        result = True
        print('exists', path)
    else:
        print('does NOT exists', path)
        result = False

    # set or update key to reset TTL
    recent_logged_paths[path]=True
    return result


def create_database(db_file):
    """ create a database connection to a SQLite database """
    connection = None
    try:
        connection = sqlite3.connect(db_file)
        print(sqlite3.version)
        cursor = connection.cursor()
        #  cursor.execute("CREATE TABLE file_changes (id INTEGER PRIMARY KEY, created_at TEXT, path TEXT, change_type TEXT)")
        cursor.execute("CREATE TABLE dir_changes (id INTEGER PRIMARY KEY  NOT NULL, path VARCHAR,created_at DATETIME,change_type VARCHAR)")

        cursor.execute("CREATE TABLE backup_logs (id INTEGER PRIMARY KEY  NOT NULL, created_at DATETIME, source_path VARCHAR, dest_path VARCHAR, command VARCHAR, log_file VARCHAR, source_file VARCHAR, run_type VARCHAR DEFAULT (null) )")

        connection.commit()

    except sqlite3.Error as e:
        print(e)
    finally:
        if connection:
            connection.close()



def log_change(cursor, filename, directory, change_type):
    """
    Logs a change to the specified directory in the database.

    Args:
        directory: The directory that was changed.
        change_type: The type of change that was made.

    """

    print ('received', filename, directory, change_type)
    #  return 

    if was_logged_recently(directory):
        return


    # Get the current date and time
    date = time.strftime("%Y-%m-%d %H:%M:%S")

    # Insert the change into the database
    cursor.execute("INSERT INTO dir_changes (id, path, created_at, change_type) VALUES (NULL, ?, ?, ?)", (directory, date, change_type.strip().lower()))
    connection.commit()
    print(f"Logged: file {filename} in {directory} changed: {change_type}")

#  https://stackoverflow.com/questions/39089776/python-read-named-pipe

if __name__ == "__main__":
    db_file = sys.argv[1]
    fifo_pipe = sys.argv[2]
    if not os.path.exists(db_file):
        create_database(db_file)
    #  log_change(db_file, directory, change_type)

    #  os.mkfifo(FIFO)
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    try:
        while True:
            with open(fifo_pipe) as fifo:
                for line in fifo:
                    log_change(cursor, *line.split(','))
    finally:
        if connection:
            connection.close()

