import os
import re
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, make_response, redirect, session, url_for
from flask_dance.contrib.github import github, make_github_blueprint

# load env
BASEDIR = Path(__file__).parents[1]
for env in (".flaskenv", ".env"):
    load_dotenv(BASEDIR / env)

USERNAME_RE = re.compile(r"^[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}$")


def button(text, url, logo=None):
    if logo:
        return f"""<a href="{url}" class="logo button">{text}</a>"""
    return f"""<a href="{url}" class="button">{text}</a>"""


class Autofork(Flask):
    def __init__(self):
        super().__init__(__name__, template_folder="static")

        self.url_map.strict_slashes = False
        self.secret_key = os.getenv("SECRET_KEY", "skeleton-key")
        self.load_config()

        github_bp = make_github_blueprint(
            scope="public_repo,read:user", login_url="/", authorized_url="/authorized"
        )
        self.register_blueprint(github_bp, url_prefix="/login")

    def load_config(self):
        origin = url = os.getenv("GITHUB_ORIGIN", "")
        if not url.endswith(".git"):
            raise ValueError(f"Invalid GitHub repo origin URL: `{url}`")

        url = url[:-4]
        if url.startswith("git@"):
            *_, user_repo = url.partition(":")
            user, _, repo = user_repo.partition("/")
            if not USERNAME_RE.match(user):
                raise ValueError(f"Invalid GitHub username: `{user}`")

            url = url.replace(":", "/").replace("git@", "https://")

        elif url.startswith("https://"):
            _, user, repo = url.rsplit("/", maxsplit=2)

        else:
            raise ValueError(f"Unsupported GitHub repo origin URL: `{url}`")

        self.config["AUTOFORK_ORIGIN"] = origin
        self.config["AUTOFORK_URL"] = url
        self.config["AUTOFORK_USER"] = user
        self.config["AUTOFORK_REPO"] = repo

        self.config["GITHUB_OAUTH_CLIENT_ID"] = os.getenv("GITHUB_OAUTH_CLIENT_ID")
        self.config["GITHUB_OAUTH_CLIENT_SECRET"] = os.getenv("GITHUB_OAUTH_CLIENT_SECRET")


app = Autofork()


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
