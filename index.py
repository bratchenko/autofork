import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, make_response, redirect, session, url_for
from flask_dance.contrib.github import github, make_github_blueprint

# load env
BASEDIR = Path(__file__).parents[1]
for env in (".flaskenv", ".env"):
    load_dotenv(BASEDIR / env)


ORIGIN = os.getenv("GITHUB_ORIGIN", "")

# app
github_bp = make_github_blueprint(
    client_id=os.getenv("GITHUB_OAUTH_CLIENT_ID", "secret-agent"),
    client_secret=os.getenv("GITHUB_OAUTH_CLIENT_SECRET", "agent-secret"),
    scope="public_repo,read:user",
    login_url="/",
    authorized_url="/authorized",
)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "skeleton-key")
app.register_blueprint(github_bp, url_prefix="/login")


def button(text, url, logo=None):
    if logo:
        return f"""<a href="{url}" class="logo button">{text}</a>"""
    return f"""<a href="{url}" class="button">{text}</a>"""


def git_to_url(text):
    if text.startswith("git@"):
        text = text.replace(":", "/").replace("git@", "https://")

    if text.startswith("https://"):
        return text[:-4] if text.endswith(".git") else text

    return make_response(f"Invalid GitHub repo origin URL: `{text}`", 500)


@app.route("/")
def index():
    body = f"""<link rel="stylesheet" href="/static/style.css" />
    <h1>Autofork</h1>
    <p>This application forks itself into authorized GitHub account.</p>
    """

    if not github.authorized:
        sign_in = button("Sign in with GitHub", url_for("github.login"), logo=True)
        return make_response(body + sign_in)

    resp = github.get("/user")
    assert resp.ok, resp.text

    login = resp.json()["login"]
    fork = button("Fork", url_for("fork"), logo=True)
    sign_out = button("Sign out", url_for("logout"))

    info = f"<div>You are @{login} on GitHub</div>"
    return make_response("".join(body, info, fork, sign_out))


@app.route("/fork")
def fork():
    return make_response("GitHub origin to fork is not specified", 500)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
