import os
from pathspec import PathSpec

def read_compareignore_file(compareignore_path):
    with open(compareignore_path, 'r') as f:
        return PathSpec.from_lines('gitwildmatch', f)

def should_ignore(path, ignore_spec):
    return ignore_spec.match_file(path)

def format_elapsed_time(elapsed_time):
    milliseconds = int(elapsed_time * 1000)
    total_seconds = int(elapsed_time)
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return {
        'milliseconds': milliseconds,
        'seconds': total_seconds,
        'minutes': minutes,
        'hours': hours
    }
