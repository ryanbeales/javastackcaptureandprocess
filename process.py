import re, os
from glob import glob
from collections import defaultdict, counter
from string import maketrans
import csv

# Our stack file input path:
stackpath = r'/apps/stack_dumps'
stackfiles = glob(os.path.join(stackpath,'jstack_*'))

# Empty list for saving stack data to

stackdata = []

# Loop through all the stack files that have been captured
for stackfile in stackfiles:
    # The filenames captured by the script are built up of these values:
    process_start_time, stack_capture_time, capture_count = stackfile.split('_')[1:]
    
    # Open the stack file and get the contents
    with open(stackfile, 'r') as f:
        stackdump = f.readlines()
    
    # Reset our thread based variables, as we're processing line by line rather
    # than stack by stack. In future we could turn this in to a multiline regex
    # to capture the stack and process the information as a block.
    # For now however, we do this.
    threadline, threadname, threadtype, threadstate = None, None, None, None
    
    for line in stackdump:
        # Each thread name starts with ". Capture the bit between the quotes to get a thread name
        if line.startswith('"'):
            threadline = line
            threadname = line.split('"')[1]
            
            # Remove any numbers from the thread name to make it a generic type:
            threadtype = threadname.translate(None, '0123456789')
        
        # The state of the thread is on the running line, but it's also on the next line starting with this:
        if threadline and line.startswith('   java.lang.Thread.State:'):
            threadstate = line.split(':')[1].strip()
        
        # If the line is blank, it means we're finished processing one of the thread stacks
        if line == '\n' and threadline and threadname and threadtype and threadstate:
            # Append all the captured data to the data list, then reset all variables for next thread
            # in the stack.
            stackdata.append([process_start_time, stack_capture_time, capture_count, threadtype, threadname, threadstate])
            threadline, threadname, threadtype, threadstate = None, None, None, None

# After all the stack dumps have been captured, dump all the captured information in to
# a csv file:
with open(os.path.join(stackpath,'jstack_analysis.csv'),'wb') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['process_start_time', 'stack_capture_time', 'capture_count', 'threadtype', 'threadname', 'threadstate'])
    csvwriter.writerows(stackdata)
