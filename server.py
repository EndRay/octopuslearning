from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def graph():
    return render_template("graph.html")


if __name__ == "__main__":
    app.run(debug=True)
