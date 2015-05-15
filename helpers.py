# Helper functions shared between these scripts

__name__ = "helpers"

import sys
import time


def print_with_timestamp(msg):
  print time.ctime() + ": " + str(msg)
  sys.stdout.flush()
# explicitly flushing stdout makes sure that a .out file stays up to date
# otherwise it can be hard to keep track of whether a background job is hanging




def elapsed_time(starttime):
  seconds = time.time() - starttime
  if seconds < 1:
    seconds = 1
  hours = int(seconds / 60 / 60)
  minutes = int(seconds / 60 - hours * 60)
  seconds = int(seconds - minutes * 60 - hours * 60 * 60)
  return (
      str(hours) + " hours, " +
      str(minutes) + " minutes and " +
      str(seconds) + " seconds"
  )
