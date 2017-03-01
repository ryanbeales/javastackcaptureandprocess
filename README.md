# Java Stack capture and Process

Bash script to capture stack dumps and Python script to process those outputs

There are two scripts in this repository:
capture.sh - A bash script to capture 10 stack dumps in a loop 10 seconds apart. At the moment it searches for a jboss standalone pid to do the stack dump.
process.py - A Python script to process those jstack captures and turn them in to CSV for further analysis.

Basic use case is to observe thread growth over time to analyise if resources/pools are scaled correctly given the amount of input traffic to the JVM.
