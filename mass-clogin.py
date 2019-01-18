#!/usr/bin/env python

import argparse
import Queue
import shlex
import subprocess
import threading

# Check the input arguments to the script
parser = argparse.ArgumentParser()
parser.add_argument('--ulist', help='File containing list of switches/routers', required=True)
parser.add_argument('--clist', help='File containing list of commands to be run', required=True)
parser.add_argument('--workers', help='Number of simultaneous workers to spawn, default is 5', default=5, type=int)
args = parser.parse_args()

hosts_file = args.ulist
command_file = args.clist
num_threads = args.workers

queue = Queue.Queue()

# Define the worker function.
def run_clogin(num_thread, queue, command_file):
    # Keep working until the main program exits
    while True:
        # Fetch a host to work on
        host = queue.get()

        # Define the command to run and run it
        clogin_command = 'clogin -x %s %s' % (command_file, host)
        p = subprocess.Popen(shlex.split(clogin_command), stdout=subprocess.PIPE)

        # Save the output from the command
        stdout, stderr = p.communicate()

        print '%s' % stdout

        # Mark the queue object as done
        queue.task_done()

# Start threads
for num_thread in range(num_threads):
    worker = threading.Thread(target=run_clogin, args=(num_thread, queue, command_file))
    worker.daemon = True
    worker.start()

# Add hosts to the queue
hosts_file_fd = open(hosts_file,"r")
for host in hosts_file_fd:
    queue.put(host.rstrip())

# Wait for the queue to be empty
queue.join()
