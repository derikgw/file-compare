import sqlite3
import os
import threading

db_lock = threading.Lock()

def store_file_in_db(db_path, file_path):
    with db_lock:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        directory, name = os.path.split(file_path)
        cursor.execute('INSERT OR IGNORE INTO directories (path) VALUES (?)', (directory,))
        cursor.execute('SELECT id FROM directories WHERE path = ?', (directory,))
        directory_id = cursor.fetchone()[0]
        cursor.execute('INSERT OR IGNORE INTO files (name, directory_id) VALUES (?, ?)', (name, directory_id))
        cursor.execute('SELECT id FROM files WHERE name = ? AND directory_id = ?', (name, directory_id))
        file_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return file_id

def store_diff_in_db(db_path, file1_id, file2_id, line_number, change_type, content):
    with db_lock:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO diffs (file1_id, file2_id, line_number, change_type, content)
            VALUES (?, ?, ?, ?, ?)
        ''', (file1_id, file2_id, line_number, change_type, content))
        conn.commit()
        conn.close()

def remove_file_from_db(db_path, file_id):
    with db_lock:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM files WHERE id = ?', (file_id,))
        conn.commit()
        conn.close()

def init_db(db_path):
    with db_lock:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS directories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                directory_id INTEGER,
                FOREIGN KEY (directory_id) REFERENCES directories(id)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS diffs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file1_id INTEGER,
                file2_id INTEGER,
                line_number INTEGER,
                change_type TEXT,
                content TEXT,
                FOREIGN KEY (file1_id) REFERENCES files(id),
                FOREIGN KEY (file2_id) REFERENCES files(id)
            )
        ''')
        conn.commit()
        conn.close()

def fetch_diff_list():
    with db_lock:
        conn = sqlite3.connect('database/compare.db')
        c = conn.cursor()
        c.execute('''
            SELECT DISTINCT f1.name, d1.path, d2.path
            FROM diffs d
            JOIN files f1 ON d.file1_id = f1.id
            JOIN files f2 ON d.file2_id = f2.id
            JOIN directories d1 ON f1.directory_id = d1.id
            JOIN directories d2 ON f2.directory_id = d2.id
        ''')
        diff_list = c.fetchall()
        conn.close()
        return diff_list

def fetch_diff_by_file_name(file_name, page, per_page):
    with db_lock:
        conn = sqlite3.connect('database/compare.db')
        c = conn.cursor()
        offset = (page - 1) * per_page
        c.execute('''
            SELECT d.content, d.change_type, d.line_number, d1.path, d2.path
            FROM diffs d
            JOIN files f1 ON d.file1_id = f1.id
            JOIN files f2 ON d.file2_id = f2.id
            JOIN directories d1 ON f1.directory_id = d1.id
            JOIN directories d2 ON f2.directory_id = d2.id
            WHERE f1.name = ? OR f2.name = ?
            ORDER BY d.line_number
            LIMIT ? OFFSET ?
        ''', (file_name, file_name, per_page, offset))
        diffs = c.fetchall()
        conn.close()

        diff_types = []
        previous_diff = None
        for diff in diffs:
            change_type = diff[1]
            diff_type = "modified"
            if previous_diff and change_type == "before" and previous_diff[1] == "after":
                diff_types[-1]['diff_type'] = "modified"
                diff_types[-1]['content'] = f"{previous_diff[0]} -> {diff[0]}"
            else:
                if change_type == "before":
                    diff_type = "removed"
                elif change_type == "after":
                    diff_type = "added"
                diff_types.append({
                    'content': diff[0],
                    'change_type': diff[1],
                    'line_number': diff[2],
                    'diff_type': diff_type
                })
            previous_diff = diff

        return diff_types
