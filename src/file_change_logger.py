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
        cursor.execute("CREATE TABLE file_changes (id INTEGER PRIMARY KEY, creaed_at TEXT, path TEXT, change_type TEXT)")
        connection.commit()

    except sqlite3.Error as e:
        print(e)
    finally:
        if connection:
            connection.close()



def log_change(db_file, filename, directory, change_type):
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

    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()

    # Get the current date and time
    date = time.strftime("%Y-%m-%d %H:%M:%S")

    # Insert the change into the database
    cursor.execute("INSERT INTO file_changes (id, date, directory, change_type) VALUES (NULL, ?, ?, ?)", (date, directory, change_type))
    connection.commit()
    print(f"Logged: file {filename} in {directory} changed: {change_type}")

#  https://stackoverflow.com/questions/39089776/python-read-named-pipe

if __name__ == "__main__":
    db_file = sys.argv[1]
    fifo = sys.argv[2]
    #  directory = sys.argv[2]
    #  change_type = sys.argv[3]
    if not os.path.exists(db_file):
        create_database(db_file)
    #  log_change(db_file, directory, change_type)

    #  FIFO = 'dir_watcher'
    #  os.mkfifo(FIFO)
    while True:
        #  print('outer loop')
        with open(fifo) as fifo:
            #  print('open fifo')
            for line in fifo:
              log_change(db_file, *line.split(','))
                #  print('change', line)

