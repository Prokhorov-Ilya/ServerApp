import csv
import os
from flask import Flask, render_template, abort
import flask_socketio as socketio


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = socketio.SocketIO(app)

def generate_table(filename):
    with open('./docs/' + filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        rows = []
        for row in reader:
            rows.append(row)
        table_html = '<table>'
        for i, row in enumerate(rows):
            table_html += '<tr>'
            for j, col in enumerate(row):
                if j == 7:  # Если это ячейка восьмого столбца
                    if i > 1:
                        if float(rows[i][4]) <= float(col) <= float(rows[i][6]):  # Если значение входит в диапазон, то зеленый
                            table_html += '<td style="background-color: green;">' + col + '</td>'
                        elif float(rows[i][4]) > float(col) or float(col) > float(rows[i][6]):  # Иначе красный
                            table_html += '<td style="background-color: red;">' + col + '</td>'
                    else:
                        table_html += '<td>' + col + '</td>'
                else:
                    table_html += '<td>' + col + '</td>'
            table_html += '</tr>'
        table_html += '</table>'
        return table_html

def update_table():
    csv_files = [f for f in os.listdir('./docs') if f.endswith('.csv')]
    last_file = max(csv_files)
    table_html = generate_table(last_file)
    socketio.emit('table_update', table_html)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    update_table()

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('table_update')
def handle_table_update():
    update_table()

@app.route('/')
def index():
    last_file = max(os.listdir('./docs'))
    table_html = generate_table(last_file)
    return render_template('template.html', content=table_html)

@app.route('/<path:path>')
def load_html(path):
    try:
        with open('templates/' + path, 'rb') as file:
            return file.read()
    except FileNotFoundError:
        abort(404)


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, port=1245, host='localhost')
