import os
import difflib
import concurrent.futures
from database.database import store_file_in_db, store_diff_in_db, remove_file_from_db


def compare_files(file1, file2, ignore_spec, db_path):
    if should_ignore(file1, ignore_spec) or should_ignore(file2, ignore_spec):
        return

    has_diff = False
    file1_id = store_file_in_db(db_path, file1)
    file2_id = store_file_in_db(db_path, file2)

    try:
        with open(file1, 'r', encoding='utf-8', errors='ignore') as f1, open(file2, 'r', encoding='utf-8',
                                                                             errors='ignore') as f2:
            content1 = f1.readlines()
            content2 = f2.readlines()
            diff = list(difflib.unified_diff(content1, content2, lineterm=''))

        for i, line in enumerate(diff):
            if line.startswith('@@') or line.startswith('--') or line.startswith('++'):
                continue
            if line.startswith('-'):
                store_diff_in_db(db_path, file1_id, file2_id, i + 1, 'before', line[1:])
                has_diff = True
            elif line.startswith('+'):
                store_diff_in_db(db_path, file1_id, file2_id, i + 1, 'after', line[1:])
                has_diff = True

        if not has_diff:
            remove_file_from_db(db_path, file1_id)
            remove_file_from_db(db_path, file2_id)

    except PermissionError as e:
        store_diff_in_db(db_path, file1_id, file2_id, None, None, str(e))


def compare_directories(dir1, dir2, ignore_spec, db_path, max_workers):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for root, _, files in os.walk(dir1):
            for file_name in files:
                file1 = os.path.join(root, file_name)
                file2 = os.path.join(dir2, os.path.relpath(file1, dir1))
                if os.path.exists(file2) and not should_ignore(file1, ignore_spec):
                    futures.append(executor.submit(compare_files, file1, file2, ignore_spec, db_path))
        for future in concurrent.futures.as_completed(futures):
            future.result()


def should_ignore(path, ignore_spec):
    return ignore_spec.match_file(path)
