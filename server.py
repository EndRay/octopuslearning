from flask import Flask, render_template, jsonify

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
def virtual_rating(handle):
    return jsonify([{"x": 1488719100, "y": 1485, "delta": -15, "contest": ["Codeforces Round #403 (Div. 2, based on Technocup 2017 Finals)"]}, {"x": 1489590300, "y": 1549, "delta": 64, "contest": ["Codeforces Round #404 (Div. 2)"]}])


if __name__ == "__main__":
    app.run(debug=True)
