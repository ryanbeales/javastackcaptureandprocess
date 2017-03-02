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
    with open(stackfiles[0], 'r') as f:
        stackdump = f.read()
    
    # Iterate over each stack found in the file
    # The regular expression here is finding any line beginning with ", up to two new
    # lines in a row. But also capturing the text between the quotes as a group. Both
    # * characters are non-greedy with ?.
    for stack in re.finditer('^"(.*?)".*?\n\n', stackdump, re.DOTALL|re.MULTILINE):
        fullstack = stack.group(0)
        threadname = stack.group(1)
        
        # Do the same genericising of the thread name
        threadtype = threadname.translate(None, '0123456789')
        
        # Find the thread state line, but if it doesn't exist, leave it as None
        threadstate_match = re.search('java.lang.Thread.State: (.*)', fullstack)
        threadstate = threadstate_match.group(1) if threadstate_match else None
            
        stackdata.append([process_start_time, stack_capture_time, capture_count, threadtype, threadname, threadstate])

# After all the stack dumps have been captured, dump all the captured information in to
# a csv file:
with open(os.path.join(stackpath,'jstack_analysis.csv'),'wb') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['process_start_time', 'stack_capture_time', 'capture_count', 'threadtype', 'threadname', 'threadstate'])
    csvwriter.writerows(stackdata)
