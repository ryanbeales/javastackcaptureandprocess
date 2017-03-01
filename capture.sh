#!/bin/bash
# Each stack dump is roughly 300k

JBOSS_PID=$(pgrep -f "\-Djboss.server.base.dir=/usr/share/jbossas/standalone")
OUTPUT_DIR="/apps/stack_dumps"

LOOPS=10
LOOP_DELAY=10

# helper functions:

# Check that we have an output directory to store in, if not, exit
function check_outdir_exists {
    if [ ! -d "${OUTPUT_DIR}" ]; then
        echo "Output directory doesn't exist. Not running."
        exit 1
    fi
}

# Check we have enough disk space free to store that output, abandon this process if not.
function check_disk_free {
    PCT_USED=$(df -h $OUTPUT_DIR | awk '/\/apps/{ gsub("%", ""); print $4}')
    
    if (( PCT_USED > 70 )); then
        echo "Not enough free disk space, not running."
        exit 2
    fi
}

# Get a timestamp for the process start to uniquely identify it (PID works, but it could be reused)
function get_process_start_timestamp {
    echo $(date -d "$(ps -p $1 -o lstart=)" +'%s')
}

# Get the jstack output for a given PID.
function get_jstack {
    OUTPUT_FILE="${OUTPUT_DIR}/jstack_$(get_process_start_timestamp $1)_$(date +%Y%m%d%H%M%S)"
    /usr/bin/jstack $1 > ${OUTPUT_FILE}_$2
}

# Loop for getting multiple jstack outputs, up to $LOOPS times with $LOOP_DELAY seconds in between
function get_multiple_jstack {
    LOOP=1
    while (( $LOOP < $LOOPS )); do
        get_jstack $1 $LOOP

        sleep $LOOP_DELAY
        LOOP=$((LOOP + 1))
    done
}

# Remove anything older than 14 days to keep the output directory clean.
function delete_old_stack_traces {
    find $OUTPUT_DIR -mtime +14 -exec rm {} \;
}


# Do our start up checks, exit the script if they fail
check_outdir_exists
check_disk_free

# Get multiple stack dumps for this run
get_multiple_jstack $JBOSS_PID

# Clean up old stack dumps
delete_old_stack_traces

# Finished.
