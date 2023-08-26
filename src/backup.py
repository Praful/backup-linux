"""
=============================================================================
File: backup.py
Description: backup directories that have changed
Author: Praful https://github.com/Praful/backup-linux
Licence: GPL v3
=============================================================================
"""
import sqlite3
import glob
import os
import time
import datetime
import argparse
import re
import sys

def setup_command_line():
    """
    Define command line switches
    """
    cmdline = argparse.ArgumentParser(
        prog='backup.py', description='Backup directories that have changed')
    cmdline.add_argument('--database', dest='database', type=str, required=True,
                         help='SQLite database file')
    cmdline.add_argument('--to', dest='dest', type=str, required=True,
                         help='Directory to copy to')
    cmdline.add_argument('--exclude', dest='exclude', type=str, required=False,
                         help='Exclude paths containing this string')
    cmdline.add_argument('--include', dest='include', type=str, required=False,
                         help='Include paths containing this regex; overrides --exclude')
    cmdline.add_argument('--verbose', action=argparse.BooleanOptionalAction,
                         default=False, help='Provides verbose output')

    return cmdline

#  RUN_CMD = 'rsync --dry-run --recursive --verbose --human-readable -P {} {}'
RUN_CMD = 'rsync --times --update --mkpath --recursive --verbose --human-readable -P {} {}'

class Backup:
    # -P = --partial --progress
    def __init__(self, database, dest_dir):
        self.database = database
        self.dest_dir = dest_dir
        #  print(self.dest_dir)
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def start(self):
        print('start')
        from_date="2000-01-01"
        processed_dirs = set()
        home_path_len = len(os.path.expanduser('~'))
        dir_changes = self.cursor.execute("select * from dir_changes where created_at >"+from_date)
        #  print(dir_changes)
        for row in dir_changes:
            print('*'*60)
            _,path,_,_ = row
            print(path)
            if path not in processed_dirs:
                rel_path = path[home_path_len+2:] # strip homepath and leading slasdd#h
                abs_dest_path = os.path.join(self.dest_dir, rel_path)
                #  print('rel', rel_path, 'dest', abs_dest_path)
                run = RUN_CMD.format(path, abs_dest_path)
                print(run)
                os.system(run)
                processed_dirs.add(path)


    def end(self):
        print('end')

        if self.connection:
            self.connection.close()

def main():
    """
    Processing begins here if script run directly
    """
    args = setup_command_line().parse_args()
    print(args)

    try:
        backup = Backup(args.database, args.dest)
        backup.start()
    finally:
        backup.end()


    #  move_files(os.path.expanduser(args.source), os.path.expanduser(
        #  args.dest), args.exclude, args.include, args.verbose)


if __name__ == '__main__':
    main()
