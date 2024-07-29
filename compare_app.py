import os
import argparse
import time
import pathspec
from core.compare.compare import compare_directories, compare_files
from database.database import init_db
from core.util.utils import read_compareignore_file, format_elapsed_time

def main():
    parser = argparse.ArgumentParser(description="Compare files or directories and generate a report.")
    parser.add_argument("path1", help="Path to the first file or directory")
    parser.add_argument("path2", help="Path to the second file or directory")
    parser.add_argument("--fc", action="store_true", help="Compare files")
    parser.add_argument("--pc", action="store_true", help="Compare directories")
    parser.add_argument("--ignorefile", help="Path to the ignore file (default: .compareignore in current directory)")
    parser.add_argument("--outputdir", help="Directory to save the output reports (default: reports)",
                        default="reports")
    parser.add_argument("--dbfile", help="Path to the SQLite database file", default="compare.db")
    parser.add_argument("--max_workers", type=int, help="Maximum number of worker threads", default=4)
    args = parser.parse_args()

    start_time = time.perf_counter()

    # Check if a database file is provided
    dbfile = args.dbfile if args.dbfile else "database/compare.db"
    init_db(dbfile)

    if args.ignorefile:
        compareignore_path = args.ignorefile
    else:
        compareignore_path = ".compareignore"

    if os.path.isfile(compareignore_path):
        ignore_spec = read_compareignore_file(compareignore_path)
    else:
        ignore_spec = pathspec.PathSpec.from_lines('gitwildmatch', [])

    if args.fc:
        if os.path.isdir(args.path1) and os.path.isdir(args.path2):
            compare_directories(args.path1, args.path2, ignore_spec, args.dbfile, args.max_workers)
        elif os.path.isfile(args.path1) and os.path.isfile(args.path2):
            compare_files(args.path1, args.path2, ignore_spec, args.dbfile)
        else:
            print("Both paths must be files or directories for file comparison.")
    elif args.pc:
        if os.path.isdir(args.path1) and os.path.isdir(args.path2):
            compare_directories(args.path1, args.path2, ignore_spec, args.dbfile, args.max_workers)
        else:
            print("Both paths must be directories for directory comparison.")
    else:
        print("You must specify either --fc for file comparison or --pc for directory comparison.")

    elapsed_time = time.perf_counter() - start_time
    formatted_time = format_elapsed_time(elapsed_time)
    print(
        f"Comparison complete in {formatted_time['hours']} hours, {formatted_time['minutes']} minutes, {formatted_time['seconds']} seconds, and {formatted_time['milliseconds']} milliseconds. Check the database '{args.dbfile}' for the reports.")


if __name__ == "__main__":
    main()
