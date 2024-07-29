from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from database.database import init_db, fetch_diff_list, fetch_diff_by_file_name
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')


@socketio.on('get_diff_list')
def handle_get_diff_list():
    diff_list = fetch_diff_list()
    emit('diff_list', {'diffs': [{'name': row[0], 'file1_path': row[1], 'file2_path': row[2]} for row in diff_list]})


@socketio.on('load_report')
def handle_load_report(data):
    file_name = data.get('name')
    page = data.get('page', 1)
    per_page = data.get('per_page', 10)
    diffs = fetch_diff_by_file_name(file_name, page, per_page)
    emit('diff_update', {'diffs': diffs})


if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True)
