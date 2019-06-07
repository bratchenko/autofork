from flask import Flask, Response

app = Flask(__name__)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    return Response(
        """
        <link rel="stylesheet" href="/static/style.css" /> <h1>Flask on Now 2.0</h1>
        <p>You are viewing a Flask application written in Python running on Now 2.0.</p>
        <p>Visit the <a href='./about'>about</a> page or view the 
        <a href='https://github.com/zeit/now-examples/tree/master/python-flask'>source code</a>.
        </p>
        """,
        mimetype="text/html",
    )
