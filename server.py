from flask import Flask, render_template, jsonify

import virtual_rating
from tasks_performance import task_performance_stats

app = Flask(__name__)


@app.route('/')
def graph():
    return render_template("graph.html")


@app.route('/task')
def root():
    return app.send_static_file('task.html')


@app.route('/api/taskPerformance/<contest>/<index>')
def task_info(contest, index):
    contest_id = int(contest)
    return jsonify(task_performance_stats(contest_id, index))


@app.route('/api/virtualRating/<handle>')
def get_virtual_rating(handle):
    return jsonify(virtual_rating.calculate(handle))


if __name__ == "__main__":
    app.run(debug=True)
