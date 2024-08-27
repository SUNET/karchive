import re
import os
import sys
import gzip
from logging.config import dictConfig

from flask import Flask, request
from git import Repo

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)

app = Flask(__name__)


class GitError(Exception):
    pass


def git_clone_repo():
    if not os.environ.get("GIT_REPO_URL"):
        app.logger.error("GIT_REPO_URL environment variable not set")
        sys.exit(1)

    if not os.path.exists("/repo"):
        repo_url = os.environ.get("GIT_REPO_URL")

    print(f"Cloning repo: {repo_url}")

    try:
        repo = Repo.clone_from(repo_url, "/repo")
    except Exception as e:
        app.logger.error(f"Error: {e}")

    app.logger.info(f"Repo cloned: {repo_url} in /repo")

    return repo


def git_commit_repo(filename, filedata, username):
    try:
        repo = Repo("/repo")

        if isinstance(filedata, bytes):
            filedata = filedata.decode("utf-8")

        with open("/repo/" + filename, "w") as f:
            f.write(filedata)

        repo.config_writer().set_value("user", "name", username).release()
        repo.config_writer().set_value("user", "email", "noc@sunet.se").release()

        repo.index.add([filename])
        app.logger.info(f"File added to index: {filename} in repo /repo")

        repo.index.commit(f"Configuration changed by: {username}")
        app.logger.info(f"File committed: {filename} in repo /repo")

        repo.remotes.origin.push()
        app.logger.info(f"File pushed: {filename} in repo /repo")
    except Exception as e:
        app.logger.error(f"Error: {e}")
        sys.exit(1)

    return True


@app.route("/commit/<filename>", methods=["PUT"])
def put(filename):
    re_strip = re.compile(r"_\.*\d{8}_\d{6}")

    try:
        filedata = gzip.decompress(request.data)

        # Header is in the format /* Commit annotation; dennis:  */ get the username
        username = re.search(
            r".+;.(\S+):.+", filedata.decode("utf-8").split("\n")[1]
        ).group(1)

        if not username:
            app.logger.error("Username not found in header")
            username = "Unknown"

    except Exception as e:
        app.logger.error(f"Error: {e}")
        return "Error", 400

    app.logger.info(f"Received file: {filename}")

    filename = filename.replace(".gz", "")
    filename = filename.replace("-re0", "")
    filename = filename.replace("-re1", "")
    filename = filename.replace("_juniper", "")
    filename = re.sub(re_strip, "", filename)

    try:
        git_commit_repo(filename, filedata, username)
    except GitError as e:
        app.logger.error(f"Error: {e}")
        return "Error", 400

    return "OK", 200


if __name__ == "__main__":
    git_clone_repo()
    app.run(debug=True)
else:
    git_clone_repo()
