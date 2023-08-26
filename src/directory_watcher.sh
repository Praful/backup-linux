#!/usr/bin/env bash

# For fifo, see
# https://unix.stackexchange.com/questions/216778/shell-script-sending-input-to-background-process

# if this script is stopped (eg using ctrl-c), the Python process will continue. To 
# stop that, use:
#  pkill -9 -f log_changes.py

# Get the path to the directory to monitor
path="$1"

# this needs to be done once to create the pipe
# mkfifo dir_watcher

fifo_pipe=dir_watcher

# start in background
python file_change_logger.py ./file_changes.db $fifo_pipe &

# pipe output to 6 to fifo; nothing special about choosing 6
exec 6> $fifo_pipe

inotifywait --exclude 'dir_watcher|file_changes.db' -mr -e modify,delete,create $path |
  #can't get --fromfile to work; lines beginning with @ not recognised
  # inotifywait --fromfile ./exclude-files.txt --exclude 'dir_watcher' -mr -e modify,delete,create $path |
while read -r directory events filename; do
  echo $filename, $directory, $events >&6
done
