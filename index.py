import json
import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, Markup, flash, make_response, redirect, render_template, session, url_for
from flask_dance.contrib.github import github, make_github_blueprint

# ENV
BASEDIR = Path(__file__).parents[1]
for env in (".flaskenv", ".env"):
    load_dotenv(BASEDIR / env)

USERNAME_RE = re.compile(r"^[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}$")


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


@app.errorhandler(500)
def handle_errors(e):
    return make_response(render_template("error.html", details=str(e)), 500)


@app.route("/")
def index():
    username = None

    if github.authorized:
        resp = github.get("/user")
        assert resp.ok, resp.text
        username = resp.json()["login"]

    return make_response(render_template("index.html", username=username))


@app.route("/fork")
def fork():
    if not github.authorized:
        flash("Not authorized. Please sign in first.", "error")
        return redirect(url_for("index"))

    cfg = app.config.get_namespace("AUTOFORK_")
    user = cfg["user"]
    repo = cfg["repo"]
    fork_ep = f"https://api.github.com/repos/{user}/{repo}/forks"

    resp = requests.post(fork_ep)
    body = resp.json()

    if resp:
        html_url = body.get("html_url")
        link = f'<a class="link" target="_blank" rel="noopener" href="{html_url}">{html_url}</a>'
        message = Markup(f"Successfully forked {repo} to {link}")
        flash(message, "info")
    else:
        message = f"Couldn't fork {fork_ep}:"
        details = json.dumps(body, indent=2)
        flash(message, "error info")
        flash(details, "details")

    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    flash("Successfully logged out", "info")
    return redirect(url_for("index"))
